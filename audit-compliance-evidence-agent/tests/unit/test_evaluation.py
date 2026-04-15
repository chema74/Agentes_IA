from __future__ import annotations

from domain.controls.models import Control
from domain.evidence.models import Evidence
from domain.mappings.models import ControlEvidenceMapping
from services.evaluation.evaluator import detect_gaps, evaluate_control_coverage, generate_findings
from services.llm.gateway import LiteLLMGateway


LLM = LiteLLMGateway("demo-model", "fallback-model")


def make_control() -> Control:
    return Control(
        id="control-1",
        scope_id="scope-1",
        code="OPS-1",
        name="Seguimiento de incidencias criticas",
        description="Debe existir seguimiento de incidencias.",
        category="incident_management",
        criticality="critical",
        expected_criterion="Tickets, owner y remediacion.",
    )


def make_evidence(insufficient: bool = False) -> Evidence:
    return Evidence(
        id="evidence-1",
        scope_id="scope-1",
        title="Export de tickets",
        source_type="ticket_export",
        source_name="tickets.csv",
        evidence_type="ticket_export",
        mime_type="text/csv",
        uploaded_by="demo-owner",
        storage_path="storage/tickets.csv",
        content_hash="hash",
        normalized_text="INC-1 abierta y criticidad alta",
        classification="ticket_export",
        sufficiency_status="insufficient" if insufficient else "sufficient",
        freshness_status="current",
    )


def make_mapping(review_status: str = "approved", confidence: float = 0.85) -> ControlEvidenceMapping:
    return ControlEvidenceMapping(
        id="map-1",
        control_id="control-1",
        evidence_id="evidence-1",
        mapping_mode="manual",
        confidence=confidence,
        rationale="Relacion valida por contenido y contexto.",
        support_excerpt="INC-1 abierta y criticidad alta",
        review_status=review_status,
    )


def test_evaluate_coverage_returns_covered_for_approved_mapping():
    coverage = evaluate_control_coverage(make_control(), [make_evidence()], [make_mapping()])
    assert coverage.coverage_status == "covered"
    assert coverage.coverage_score >= 0.8


def test_detect_gaps_returns_owner_and_missing_evidence_when_uncovered():
    control = make_control().model_copy(update={"owner_user_id": None})
    coverage = evaluate_control_coverage(control, [], [])
    gaps = detect_gaps(control, [], coverage, has_open_remediation=False)
    gap_types = {gap.gap_type for gap in gaps}
    assert "control_without_owner" in gap_types
    assert "missing_evidence" in gap_types


def test_generate_findings_requires_human_review_for_critical_gap():
    control = make_control()
    coverage = evaluate_control_coverage(control, [], [])
    gaps = detect_gaps(control, [], coverage, has_open_remediation=False)
    findings = generate_findings(control, [], gaps, LLM)
    assert findings
    assert any(item.human_review_required for item in findings)
    assert any(item.severity in {"high", "critical"} for item in findings)
