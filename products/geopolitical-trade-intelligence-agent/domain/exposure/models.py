from __future__ import annotations

from pydantic import BaseModel


class TradeExposureMap(BaseModel):
    country: str
    sector: str
    product: str | None = None
    route: str | None = None
    exposure_level: str
    vulnerability_notes: str
