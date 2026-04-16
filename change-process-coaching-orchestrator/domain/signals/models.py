from __future__ import annotations

from pydantic import BaseModel


class ChangeSignal(BaseModel):
    signal_id: str
    category: str
    summary: str
    intensity: str
    source: str
