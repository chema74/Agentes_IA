from __future__ import annotations

from datetime import datetime, UTC

from pydantic import BaseModel, Field


class AuditPackage(BaseModel):
    id: str
    scope_id: str
    name: str
    status: str
    summary_json: dict = Field(default_factory=dict)
    storage_path: str | None = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
