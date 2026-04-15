from __future__ import annotations

from datetime import datetime, UTC
from pydantic import BaseModel, Field


class RiskEvent(BaseModel):
    user_id: str
    inferred_risk_level: str
    escalation_status: str
    matched_signals: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
