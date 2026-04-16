from __future__ import annotations

from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.progress.models import ChangeFatigueAlert
from domain.resistance.models import ResistanceProfile
from domain.signals.models import ChangeSignal


def analyze_friction(signals: list[ChangeSignal]) -> tuple[ResistanceProfile, list[AdoptionBlocker], FrictionAssessment, ChangeFatigueAlert]:
    high_count = sum(1 for item in signals if item.intensity == "high")
    medium_count = sum(1 for item in signals if item.intensity == "medium")
    resistance_type = "legitimate_concern"
    if any(item.category == "interpersonal_conflict" for item in signals):
        resistance_type = "interpersonal_conflict"
    elif any(item.category == "fatigue" for item in signals):
        resistance_type = "overload"
    intensity = "high" if high_count >= 2 else "medium" if medium_count or high_count else "low"
    blockers = [
        AdoptionBlocker(blocker="clarity_gap", impact="moderate", recommended_response="Clarify sequence and responsibilities.")
        if any(item.category == "ambiguity" for item in signals)
        else None,
        AdoptionBlocker(blocker="execution_block", impact="critical" if any(item.category == "execution_block" for item in signals) else "moderate", recommended_response="Remove operational blocker and re-sequence work.")
        if any(item.category == "execution_block" for item in signals)
        else None,
    ]
    blockers = [item for item in blockers if item is not None]
    level = "high" if high_count >= 2 else "medium" if high_count or medium_count else "low"
    process_status = "comprometido" if level == "high" else "en_friccion" if level == "medium" else "en_observacion"
    fatigue = ChangeFatigueAlert(level="high" if any(item.category == "fatigue" and item.intensity == "high" for item in signals) else "low", evidence="Detected fatigue and overload signals." if any(item.category == "fatigue" for item in signals) else "No strong fatigue signal.")
    resistance = ResistanceProfile(resistance_type=resistance_type, intensity=intensity, rationale="Resistance profile derived from repeated friction signals.")
    friction = FrictionAssessment(level=level, confidence=0.85 if signals else 0.35, process_status=process_status)
    return resistance, blockers, friction, fatigue
