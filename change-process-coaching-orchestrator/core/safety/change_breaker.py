from __future__ import annotations

from pydantic import BaseModel, Field

from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.progress.models import ChangeFatigueAlert
from domain.resistance.models import ResistanceProfile


class CircuitBreakerDecision(BaseModel):
    level: int
    status: str
    reason_codes: list[str] = Field(default_factory=list)
    human_review_required: bool
    notes: list[str] = Field(default_factory=list)


def evaluate_change_breaker(
    friction: FrictionAssessment,
    resistance: ResistanceProfile,
    blockers: list[AdoptionBlocker],
    fatigue: ChangeFatigueAlert,
) -> CircuitBreakerDecision:
    reasons: list[str] = []
    if friction.confidence < 0.45:
        reasons.append("LOW_DIAGNOSTIC_CONFIDENCE")
    if fatigue.level == "high":
        reasons.append("CHANGE_FATIGUE_HIGH")
    if any(item.impact == "critical" for item in blockers):
        reasons.append("PERSISTENT_ADOPTION_BLOCKER")
    if resistance.resistance_type in {"interpersonal_conflict", "overload"} and resistance.intensity == "high":
        reasons.append("HUMAN_INTENSIVE_CASE")
    if reasons:
        return CircuitBreakerDecision(level=4, status="circuit_breaker", reason_codes=reasons, human_review_required=True, notes=["La automatizacion debe detenerse y escalar a supervision humana."])
    if friction.level == "high":
        return CircuitBreakerDecision(level=3, status="change_compromised", reason_codes=["CHANGE_COMPROMISED"], human_review_required=True, notes=["El proceso esta comprometido y requiere rediseño o revision humana."])
    if friction.level == "medium":
        return CircuitBreakerDecision(level=2, status="relevant_friction", human_review_required=False, notes=["La friccion es relevante, pero aun intervenible de forma proporcional."])
    return CircuitBreakerDecision(level=1, status="observation", human_review_required=False, notes=["El proceso se mantiene en observacion y seguimiento ligero."])
