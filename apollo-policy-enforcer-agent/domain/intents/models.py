from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TypedIntent(BaseModel):
    intent_id: str
    action_type: str
    target_resource: str
    actor_id: str
    amount: float | None = None
    currency: str | None = None
    data_domain: str | None = None
    jurisdiction: str | None = None
    confidence_score: float
    source_text: str
    extracted_attributes: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
