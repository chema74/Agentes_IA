from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class EvidenceTrace(BaseModel):
    id: str
    student_id: str
    objective_id: str
    source_type: str
    activity_type: str
    artifact_ref: str
    draft_count: int
    revision_markers: list[str]
    time_spent_estimate: float
    quality_markers: list[str]
    stability_markers: list[str]
    process_summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
