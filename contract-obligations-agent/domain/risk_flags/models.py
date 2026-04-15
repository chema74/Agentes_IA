from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

from domain.clauses.models import EvidenceRef


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Alert(BaseModel):
    alert_id: str
    title: str
    message: str
    severity: RiskLevel
    human_review_required: bool = False
    rationale: str = ""
    evidence: list[EvidenceRef] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    overall_level: RiskLevel
    alerts: list[Alert] = Field(default_factory=list)

