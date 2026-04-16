from __future__ import annotations

from pydantic import BaseModel, Field


class TransformationMilestone(BaseModel):
    milestone: str
    status: str
    evidence: str = ""
    owner: str = "responsable_del_cambio"


class ChangeFatigueAlert(BaseModel):
    level: str
    evidence: str
    contributors: list[str] = Field(default_factory=list)
    confidence: float = 0.7


class HumanSupervisionGate(BaseModel):
    status: str
    owner: str
    rationale: str
    next_review_action: str = ""
    automation_allowed: bool = True
