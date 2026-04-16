from __future__ import annotations

from pydantic import BaseModel, Field


class EnforcementPayload(BaseModel):
    request_text: str
    actor_id: str
    target_resource: str
    context: dict = Field(default_factory=dict)
