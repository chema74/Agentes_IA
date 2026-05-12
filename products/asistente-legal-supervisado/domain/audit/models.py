from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    id: str
    reference: str
    entity_type: str
    entity_id: str
    action: str
    payload: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
