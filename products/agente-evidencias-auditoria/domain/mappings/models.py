from __future__ import annotations

from datetime import datetime, UTC

from pydantic import BaseModel, Field


class ControlEvidenceMapping(BaseModel):
    id: str
    control_id: str
    evidence_id: str
    mapping_mode: str
    confidence: float
    rationale: str
    support_excerpt: str
    review_status: str = "pending_review"
    reviewed_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CoverageEvaluation(BaseModel):
    id: str
    control_id: str
    scope_id: str
    coverage_status: str
    coverage_score: float
    explanation: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evaluated_by_system: bool = True
