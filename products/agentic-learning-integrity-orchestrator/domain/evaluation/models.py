from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class EvaluationEvent(BaseModel):
    id: str
    student_id: str
    objective_id: str
    submission_id: str
    rubric_snapshot: list[str]
    evidence_refs: list[str]
    performance_summary: str
    confidence_score: float
    evaluation_state: str
    teacher_review_required: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
