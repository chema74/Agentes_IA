from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class TeacherOverride(BaseModel):
    id: str
    evaluation_event_id: str
    teacher_id: str
    original_system_recommendation: str
    teacher_decision: str
    justification: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
