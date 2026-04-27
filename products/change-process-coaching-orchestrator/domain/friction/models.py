from __future__ import annotations

from pydantic import BaseModel, Field


class AdoptionBlocker(BaseModel):
    blocker: str
    blocker_type: str = "operational"
    impact: str
    recommended_response: str
    owner: str = "responsable_del_cambio"
    evidence: str = ""
    escalation_hint: str = ""


class FrictionAssessment(BaseModel):
    level: str
    confidence: float
    process_status: str
    friction_sources: list[str] = Field(default_factory=list)
    adoption_maturity: str = "emergent"
    discourse_execution_gap: str = "low"
    difficult_conversations_pending: bool = False
