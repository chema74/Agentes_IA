from __future__ import annotations

from pydantic import BaseModel


class TransformationMilestone(BaseModel):
    milestone: str
    status: str


class ChangeFatigueAlert(BaseModel):
    level: str
    evidence: str


class HumanSupervisionGate(BaseModel):
    status: str
    owner: str
    rationale: str
