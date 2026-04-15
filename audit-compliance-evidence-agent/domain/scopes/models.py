from __future__ import annotations

from datetime import date, datetime, UTC

from pydantic import BaseModel, Field


class AuditScope(BaseModel):
    id: str
    name: str
    description: str = ""
    framework: str = ""
    status: str = "draft"
    period_start: date | None = None
    period_end: date | None = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
