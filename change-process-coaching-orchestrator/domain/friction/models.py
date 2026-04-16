from __future__ import annotations

from pydantic import BaseModel


class AdoptionBlocker(BaseModel):
    blocker: str
    impact: str
    recommended_response: str


class FrictionAssessment(BaseModel):
    level: str
    confidence: float
    process_status: str
