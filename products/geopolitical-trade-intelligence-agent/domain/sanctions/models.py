from __future__ import annotations

from pydantic import BaseModel


class SanctionEvent(BaseModel):
    event_id: str
    category: str
    impact: str
    description: str
