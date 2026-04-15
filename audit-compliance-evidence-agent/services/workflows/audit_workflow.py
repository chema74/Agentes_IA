from __future__ import annotations

from uuid import uuid4

from connectors.files.loader import load_bytes
from core.audit.events import make_audit_event
from core.config.settings import settings
from core.db.repository import STORE
from core.security.files import validate_upload
from core.security.hashing import sha256_bytes
from domain.controls.models import Control
from domain.evidence.models import Evidence, EvidenceArtifact
from domain.packages.models import AuditPackage
from domain.remediation.models import Remediation
from domain.scopes.models import AuditScope
from services.evaluation.evaluator import detect_gaps, evaluate_control_coverage, generate_findings
from services.exports.exporter import build_audit_package_zip
from services.llm.gateway import LiteLLMGateway
from services.mapping.mapper import suggest_mapping
from services.parsing.parser import parse_loaded_file
from services.storage.storage_service import StorageService


class AuditWorkflowService:
    def __init__(self) -> None:
        self.store = STORE
        self.llm = LiteLLMGateway(settings.litellm_model, settings.litellm_fallback_model)
        self.storage = StorageService()
        self.audit_events: list[dict] = []

    def create_scope(self, scope: AuditScope) -> AuditScope:
        self.store.scopes[scope.id] = scope
        self.audit_events.append(make_audit_event("AUDIT_SCOPE", scope.id, "created", scope.created_by, {"name": scope.name}))
        return scope

    def create_control(self, control: Control, actor_user_id: str | None = None) -> Control:
        self.store.controls[control.id] = control
        self.audit_events.append(make_audit_event("CONTROL", control.id, "created", actor_user_id, {"code": control.code}))
        return control

    def ingest_evidence(self, scope_id: str, filename: str, content: bytes, uploaded_by: str, source_type: str = "manual_upload", source_name: str | None = None) -> Evidence:
        validate_upload(filename, len(content))
        loaded = load_bytes(filename, content)
        normalized_text, metadata = parse_loaded_file(loaded, redact=settings.redaction_enabled)
        storage_path = self.storage.store_evidence(f"{scope_id}/{filename}", content)
        evidence_id = f"evidence-{uuid4().hex[:12]}"
        evidence = Evidence(
            id=evidence_id,
            scope_id=scope_id,
            title=filename,
            description=f"Evidencia cargada desde {source_type}.",
            source_type=source_type,
            source_name=source_name or filename,
            source_author=None,
            evidence_type=metadata.get("classification", "unknown"),
            mime_type=loaded.suffix or "application/octet-stream",
            uploaded_by=uploaded_by,
            storage_path=storage_path,
            content_hash=sha256_bytes(content),
            normalized_text=normalized_text,
            metadata_json=metadata,
            classification=metadata.get("classification", "unknown"),
            sufficiency_status=metadata.get("sufficiency_status", "unknown"),
            freshness_status="current",
            artifacts=[
                EvidenceArtifact(
                    id=f"artifact-{uuid4().hex[:12]}",
                    evidence_id=evidence_id,
                    file_name=filename,
                    storage_path=storage_path,
                    mime_type=loaded.suffix or "application/octet-stream",
                    size_bytes=len(content),
                    sha256=sha256_bytes(content),
                    preview_text=normalized_text[:200] or None,
                )
            ],
        )
        self.store.evidence[evidence.id] = evidence
        self.audit_events.append(make_audit_event("EVIDENCE", evidence.id, "ingested", uploaded_by, {"scope_id": scope_id}))
        return evidence

    def suggest_mappings_for_scope(self, scope_id: str) -> list:
        controls = [item for item in self.store.controls.values() if item.scope_id == scope_id]
        evidence_items = [item for item in self.store.evidence.values() if item.scope_id == scope_id]
        results = []
        for control in controls:
            for evidence in evidence_items:
                mapping = suggest_mapping(control, evidence, self.llm)
                if mapping:
                    self.store.mappings[mapping.id] = mapping
                    results.append(mapping)
        return results

    def review_mapping(self, mapping_id: str, reviewed_by: str, approved: bool) -> None:
        mapping = self.store.mappings[mapping_id]
        mapping.review_status = "approved" if approved else "rejected"
        mapping.reviewed_by = reviewed_by
        self.audit_events.append(make_audit_event("CONTROL_EVIDENCE_MAPPING", mapping.id, "reviewed", reviewed_by, {"approved": approved}))

    def evaluate_scope(self, scope_id: str) -> dict:
        controls = [item for item in self.store.controls.values() if item.scope_id == scope_id]
        remediations = [item for item in self.store.remediations.values() if item.scope_id == scope_id and item.status != "done"]
        coverage_results = []
        all_gaps = []
        all_findings = []
        finding_control_map = {finding.id: finding.control_id for finding in self.store.findings.values() if finding.scope_id == scope_id}
        for control in controls:
            control_mappings = [item for item in self.store.mappings.values() if item.control_id == control.id]
            evidence_items = [self.store.evidence[item.evidence_id] for item in control_mappings if item.evidence_id in self.store.evidence]
            coverage = evaluate_control_coverage(control, evidence_items, control_mappings)
            self.store.coverage[coverage.id] = coverage
            gaps = detect_gaps(
                control,
                evidence_items,
                coverage,
                has_open_remediation=any(finding_control_map.get(rem.finding_id) == control.id for rem in remediations),
            )
            for gap in gaps:
                self.store.gaps[gap.id] = gap
            findings = generate_findings(control, evidence_items, gaps, self.llm)
            for finding in findings:
                self.store.findings[finding.id] = finding
            coverage_results.append(coverage)
            all_gaps.extend(gaps)
            all_findings.extend(findings)
        return {"coverage": coverage_results, "gaps": all_gaps, "findings": all_findings}

    def create_remediation(self, remediation: Remediation, actor_user_id: str | None = None) -> Remediation:
        self.store.remediations[remediation.id] = remediation
        self.audit_events.append(make_audit_event("REMEDIATION", remediation.id, "created", actor_user_id, {"finding_id": remediation.finding_id}))
        return remediation

    def export_package(self, scope_id: str, created_by: str) -> AuditPackage:
        scope = self.store.scopes[scope_id]
        controls = [item.model_dump(mode="json") for item in self.store.controls.values() if item.scope_id == scope_id]
        evidence_items = [item.model_dump(mode="json") for item in self.store.evidence.values() if item.scope_id == scope_id]
        gaps = [item.model_dump(mode="json") for item in self.store.gaps.values() if item.scope_id == scope_id]
        findings = [item.model_dump(mode="json") for item in self.store.findings.values() if item.scope_id == scope_id]
        remediations = [item.model_dump(mode="json") for item in self.store.remediations.values() if item.scope_id == scope_id]
        traceability = {mapping.id: mapping.model_dump(mode="json") for mapping in self.store.mappings.values() if self.store.controls[mapping.control_id].scope_id == scope_id}
        package_id = f"package-{uuid4().hex[:12]}"
        payload = {
            "package_name": f"Audit package {scope.name}",
            "scope": scope.model_dump(mode="json"),
            "controls": controls,
            "evidence": evidence_items,
            "gaps": gaps,
            "findings": findings,
            "remediations": remediations,
            "traceability": traceability,
        }
        zip_bytes = build_audit_package_zip(payload)
        storage_path = self.storage.store_package(f"{scope_id}/{package_id}.zip", zip_bytes)
        package = AuditPackage(id=package_id, scope_id=scope_id, name=payload["package_name"], status="generated", summary_json={"controls": len(controls), "findings": len(findings)}, storage_path=storage_path, created_by=created_by)
        self.store.packages[package.id] = package
        self.audit_events.append(make_audit_event("AUDIT_PACKAGE", package.id, "exported", created_by, {"scope_id": scope_id}))
        return package


WORKFLOW = AuditWorkflowService()
