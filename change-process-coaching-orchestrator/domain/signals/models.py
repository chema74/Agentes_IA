from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ChangeSignal(BaseModel):
    signal_id: str
    category: str
    summary: str
    intensity: str
    source: str
    domain: str = "change_process"
    evidence_excerpt: str = ""
    interpretation_status: str = "observed"
    confidence: float = 0.7
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
