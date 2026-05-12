from __future__ import annotations

from pydantic import BaseModel, Field

from domain.routes.models import RouteDisruptionAlert
from domain.sanctions.models import SanctionEvent


class TradeBreakerDecision(BaseModel):
    level: int
    status: str
    reason_codes: list[str] = Field(default_factory=list)
    human_review_required: bool


def evaluate_trade_breaker(
    sanctions: list[SanctionEvent],
    route_alerts: list[RouteDisruptionAlert],
    confidence: float,
    country_risk_score: int,
) -> TradeBreakerDecision:
    reasons: list[str] = []
    if sanctions:
        reasons.append("SANCTION_OR_RESTRICTION_DETECTED")
    if any(item.severity == "critical" for item in route_alerts):
        reasons.append("CRITICAL_ROUTE_DISRUPTION")
    if country_risk_score >= 8:
        reasons.append("SEVERE_COUNTRY_RISK")
    if confidence < 0.45:
        reasons.append("INSUFFICIENT_CONFIDENCE")
    if reasons:
        return TradeBreakerDecision(level=4, status="circuit_breaker", reason_codes=reasons, human_review_required=True)
    if country_risk_score >= 6 or any(item.severity == "high" for item in route_alerts):
        return TradeBreakerDecision(level=3, status="significant_risk", reason_codes=["REQUIRES_EXECUTIVE_REVIEW"], human_review_required=True)
    if country_risk_score >= 4:
        return TradeBreakerDecision(level=2, status="commercial_alert", human_review_required=False)
    return TradeBreakerDecision(level=1, status="context_observation", human_review_required=False)
