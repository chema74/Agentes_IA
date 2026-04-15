from __future__ import annotations

from uuid import uuid4

from domain.controls.models import Control
from domain.evidence.models import Evidence
from domain.findings.models import Finding, FindingEvidenceLink
from domain.gaps.models import Gap
from domain.mappings.models import ControlEvidenceMapping, CoverageEvaluation
from services.llm.gateway import LiteLLMGateway


def evaluate_control_coverage(control: Control, evidence_items: list[Evidence], mappings: list[ControlEvidenceMapping]) -> CoverageEvaluation:
    if not mappings:
        return CoverageEvaluation(
            id=f"cov-{uuid4().hex[:12]}",
            control_id=control.id,
            scope_id=control.scope_id,
            coverage_status="not_covered",
            coverage_score=0.0,
            explanation="No hay mapeos entre el control y evidencias.",
        )
    reviewed = [mapping for mapping in mappings if mapping.review_status in {"approved", "pending_review"}]
    avg_confidence = sum(mapping.confidence for mapping in reviewed) / len(reviewed) if reviewed else 0.0
    if not reviewed:
        status = "not_verifiable"
    elif any(item.sufficiency_status == "insufficient" for item in evidence_items):
        status = "partially_covered"
    elif avg_confidence >= 0.75:
        status = "covered"
    else:
        status = "partially_covered"
    return CoverageEvaluation(
        id=f"cov-{uuid4().hex[:12]}",
        control_id=control.id,
        scope_id=control.scope_id,
        coverage_status=status,
        coverage_score=round(avg_confidence, 2),
        explanation=f"Cobertura calculada con {len(reviewed)} mapeos revisables y confianza media {avg_confidence:.2f}.",
    )


def detect_gaps(control: Control, evidence_items: list[Evidence], coverage: CoverageEvaluation, has_open_remediation: bool) -> list[Gap]:
    gaps: list[Gap] = []
    if control.owner_user_id is None:
        gaps.append(Gap(id=f"gap-{uuid4().hex[:12]}", scope_id=control.scope_id, control_id=control.id, gap_type="control_without_owner", severity="medium", explanation="El control no tiene owner asignado.", human_review_required=True))
    if coverage.coverage_status == "not_covered":
        gaps.append(Gap(id=f"gap-{uuid4().hex[:12]}", scope_id=control.scope_id, control_id=control.id, gap_type="missing_evidence", severity="high" if control.criticality in {"high", "critical"} else "medium", explanation="No existe evidencia vinculada al control.", human_review_required=True))
    if any(item.sufficiency_status == "insufficient" for item in evidence_items):
        gaps.append(Gap(id=f"gap-{uuid4().hex[:12]}", scope_id=control.scope_id, control_id=control.id, gap_type="insufficient_evidence", severity="medium", explanation="La evidencia existente es insuficiente o vacia.", human_review_required=True))
    if any(item.freshness_status == "stale" for item in evidence_items):
        gaps.append(Gap(id=f"gap-{uuid4().hex[:12]}", scope_id=control.scope_id, control_id=control.id, gap_type="stale_evidence", severity="medium", explanation="La evidencia parece obsoleta.", human_review_required=True))
    if has_open_remediation:
        gaps.append(Gap(id=f"gap-{uuid4().hex[:12]}", scope_id=control.scope_id, control_id=control.id, gap_type="pending_remediation", severity="medium", explanation="Existe una remediacion pendiente relacionada con el control.", human_review_required=False))
    return gaps


def generate_findings(control: Control, evidence_items: list[Evidence], gaps: list[Gap], llm: LiteLLMGateway) -> list[Finding]:
    findings: list[Finding] = []
    for gap in gaps:
        severity = "critical" if control.criticality == "critical" and gap.gap_type == "missing_evidence" else gap.severity
        finding = Finding(
            id=f"finding-{uuid4().hex[:12]}",
            scope_id=control.scope_id,
            control_id=control.id,
            title=f"Hallazgo para {control.code}",
            severity=severity,
            explanation=gap.explanation,
            confidence=0.85 if severity in {"high", "critical"} else 0.7,
            preliminary_recommendation=llm.propose_finding_recommendation(gap.gap_type),
            human_review_required=True if severity in {"high", "critical"} or gap.human_review_required else False,
        )
        for evidence in evidence_items[:3]:
            finding.evidence_links.append(FindingEvidenceLink(id=f"fel-{uuid4().hex[:12]}", finding_id=finding.id, evidence_id=evidence.id, relationship_type="supporting", commentary=evidence.title))
        findings.append(finding)
    return findings
