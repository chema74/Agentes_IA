from __future__ import annotations

from uuid import uuid4

from domain.controls.models import Control
from domain.evidence.models import Evidence
from domain.mappings.models import ControlEvidenceMapping
from services.llm.gateway import LiteLLMGateway


def suggest_mapping(control: Control, evidence: Evidence, llm: LiteLLMGateway) -> ControlEvidenceMapping | None:
    evidence_text = f"{evidence.title} {evidence.description} {evidence.normalized_text}".lower()
    terms = [token for token in control.name.lower().split() if len(token) > 3]
    score = sum(1 for token in terms if token in evidence_text)
    if score == 0:
        return None
    confidence = min(0.95, 0.35 + (0.1 * score))
    return ControlEvidenceMapping(
        id=f"map-{uuid4().hex[:12]}",
        control_id=control.id,
        evidence_id=evidence.id,
        mapping_mode="automatic_assisted",
        confidence=confidence,
        rationale=llm.propose_mapping_rationale(control.description, evidence_text),
        support_excerpt=evidence.normalized_text[:240],
        review_status="pending_review",
    )
