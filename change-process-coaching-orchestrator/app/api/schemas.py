from __future__ import annotations

from pydantic import BaseModel


class ChangeCasePayload(BaseModel):
    process_notes: str
    context_type: str = "organizational"
