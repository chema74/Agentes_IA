from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from domain.intents.models import TypedIntent


class ActionMandate(BaseModel):
    mandate_id: str
    typed_intent: TypedIntent
    decision: str
    constraints_applied: list[str] = Field(default_factory=list)
    actor_id: str
    target_resource: str
    explanation: str
    audit_reference: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
