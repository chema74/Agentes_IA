from __future__ import annotations

from datetime import date, datetime, UTC

from pydantic import BaseModel, Field


class Remediation(BaseModel):
    id: str
    scope_id: str
    finding_id: str
    title: str
    description: str
    status: str = "proposed"
    owner_user_id: str | None = None
    target_date: date | None = None
    completion_note: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
