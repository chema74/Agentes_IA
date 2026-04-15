from __future__ import annotations

from domain.controls.models import Control
from domain.evidence.models import Evidence
from services.llm.gateway import LiteLLMGateway
from services.mapping.mapper import suggest_mapping


LLM = LiteLLMGateway("demo-model", "fallback-model")


def build_control() -> Control:
    return Control(
        id="c1",
        scope_id="scope-1",
        code="A.1",
        name="Revision de accesos privilegiados",
        description="Revisar accesos privilegiados y conservar evidencia.",
        category="access_management",
        criticality="high",
        expected_criterion="Debe existir revision y evidencia.",
    )


def build_evidence(text: str) -> Evidence:
    return Evidence(
        id="e1",
        scope_id="scope-1",
        title="Revision trimestral de accesos",
        source_type="manual_upload",
        source_name="revision.txt",
        evidence_type="policy",
        mime_type="text/plain",
        uploaded_by="demo-owner",
        storage_path="demo/revision.txt",
        content_hash="abc",
        normalized_text=text,
        classification="policy",
        sufficiency_status="sufficient",
        freshness_status="current",
    )


def test_suggest_mapping_returns_mapping_when_terms_overlap():
    mapping = suggest_mapping(build_control(), build_evidence("La revision de accesos privilegiados fue aprobada."), LLM)
    assert mapping is not None
    assert mapping.confidence >= 0.45
    assert mapping.mapping_mode == "automatic_assisted"


def test_suggest_mapping_returns_none_without_overlap():
    evidence = build_evidence("Inventario de portatiles actualizado. Ninguna cuenta elevada revisada.")
    evidence.title = "Inventario de activos"
    mapping = suggest_mapping(build_control(), evidence, LLM)
    assert mapping is None
