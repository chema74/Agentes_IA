from __future__ import annotations

from datetime import datetime, UTC

from pydantic import BaseModel, Field


class Control(BaseModel):
    id: str
    scope_id: str
    code: str
    name: str
    description: str
    category: str
    criticality: str
    expected_criterion: str
    status: str = "draft"
    owner_user_id: str | None = None
    version: str = "1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
