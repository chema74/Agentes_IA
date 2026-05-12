from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class IntegrityAlert(BaseModel):
    id: str
    student_id: str
    evaluation_event_id: str
    signal_level: int
    signal_type: str
    description: str
    supporting_evidence_refs: list[str]
    confidence_score: float
    circuit_breaker_triggered: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
