from __future__ import annotations

from pydantic import BaseModel


class GeopoliticalSignal(BaseModel):
    signal_id: str
    category: str
    country: str
    summary: str
    intensity: str
