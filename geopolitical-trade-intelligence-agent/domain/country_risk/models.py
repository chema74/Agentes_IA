from __future__ import annotations

from pydantic import BaseModel


class CountryRiskProfile(BaseModel):
    country: str
    political_risk: int
    regulatory_risk: int
    geopolitical_risk: int
    summary: str
