from __future__ import annotations

from pydantic import BaseModel


class TradeCasePayload(BaseModel):
    signal_text: str
    country: str
    sector: str
    product: str | None = None
    route: str | None = None
