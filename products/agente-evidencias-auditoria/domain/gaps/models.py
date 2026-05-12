from __future__ import annotations

from datetime import datetime, UTC

from pydantic import BaseModel, Field


class Gap(BaseModel):
    id: str
    scope_id: str
    control_id: str
    gap_type: str
    severity: str
    explanation: str
    human_review_required: bool
    status: str = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
