from __future__ import annotations

from pydantic import BaseModel


class MessageRequest(BaseModel):
    user_id: str
    message: str


class OrchestratorResponse(BaseModel):
    affective_state: dict
    inferred_risk_level: str
    continuity_notes: str
    validated_signals: list[str]
    intervention_style: str
    recommended_next_step: str
    escalation_status: str
    safety_notes: list[str]
    narrative_memory_reference: list[str]
    response_text: str
