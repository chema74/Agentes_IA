from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class LearningObjective(BaseModel):
    id: str
    course_id: str
    title: str
    description: str
    rubric_criteria: list[str]
    expected_evidence_patterns: list[str]
    difficulty_level: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
