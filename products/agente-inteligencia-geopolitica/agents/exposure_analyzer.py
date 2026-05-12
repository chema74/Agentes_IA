from __future__ import annotations

from domain.country_risk.models import CountryRiskProfile
from domain.exposure.models import TradeExposureMap
from domain.signals.models import GeopoliticalSignal


def analyze_exposure(country: str, sector: str, product: str | None, route: str | None, signals: list[GeopoliticalSignal]) -> tuple[CountryRiskProfile, TradeExposureMap]:
    score = 3
    if any(item.category == "sanction" for item in signals):
        score += 4
    if any(item.category == "trade_policy" for item in signals):
        score += 2
    if any(item.category == "country_risk" for item in signals):
        score += 1
    score = min(score, 10)
    profile = CountryRiskProfile(
        country=country,
        political_risk=min(10, score),
        regulatory_risk=min(10, score + 1),
        geopolitical_risk=min(10, score + (1 if any(item.category == "country_risk" for item in signals) else 0)),
        summary=f"Perfil preliminar de riesgo para {country} con score agregado {score}/10.",
    )
    exposure = TradeExposureMap(
        country=country,
        sector=sector,
        product=product,
        route=route,
        exposure_level="high" if score >= 7 else "medium" if score >= 4 else "low",
        vulnerability_notes="Exposure adjusted for country, sector and signal convergence.",
    )
    return profile, exposure
