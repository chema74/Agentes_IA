from __future__ import annotations

from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.progress.models import ChangeFatigueAlert
from domain.resistance.models import ResistanceProfile
from domain.signals.models import ChangeSignal


def analyze_friction(signals: list[ChangeSignal]) -> tuple[ResistanceProfile, list[AdoptionBlocker], FrictionAssessment, ChangeFatigueAlert]:
    high_count = sum(1 for item in signals if item.intensity == "high")
    medium_count = sum(1 for item in signals if item.intensity == "medium")
    categories = {item.category for item in signals}
    resistance_type = "legitimate_concern"
    legitimacy = "legitimate"
    manifestations: list[str] = []
    if "interpersonal_conflict" in categories:
        resistance_type = "interpersonal_conflict"
        manifestations.append("conflicto interpersonal relevante")
    elif "fatigue" in categories:
        resistance_type = "overload"
        manifestations.append("sobrecarga y fatiga de cambio")
    elif "ambiguity" in categories:
        manifestations.append("ambiguedad sostenida")
    if "execution_block" in categories:
        manifestations.append("bloqueo operativo")
    if "passive_resistance" in categories:
        resistance_type = "passive_resistance"
        legitimacy = "mixed"
        manifestations.append("resistencia pasiva")
    intensity = "high" if high_count >= 2 else "medium" if medium_count or high_count else "low"
    blockers = [
        AdoptionBlocker(
            blocker="clarity_gap",
            blocker_type="clarity",
            impact="moderate",
            recommended_response="Clarify sequence, responsibilities, and near-term decision rights.",
            owner="responsable_del_cambio",
            evidence="Repeated ambiguity signals were detected.",
            escalation_hint="Escalar si la ambiguedad persiste tras una conversacion de aclaracion.",
        )
        if "ambiguity" in categories
        else None,
        AdoptionBlocker(
            blocker="execution_block",
            blocker_type="operational",
            impact="critical" if "execution_block" in categories else "moderate",
            recommended_response="Remove the operational blocker and re-sequence adoption steps.",
            owner="lider_de_area",
            evidence="Execution blockers and delays are affecting adoption continuity.",
            escalation_hint="Escalar si el bloqueo compromete capacidad o fecha critica.",
        )
        if "execution_block" in categories
        else None,
        AdoptionBlocker(
            blocker="difficult_conversation_pending",
            blocker_type="relational",
            impact="high",
            recommended_response="Open a facilitated difficult conversation before adding more tasks.",
            owner="responsable_humano",
            evidence="Conflict signals indicate relational friction.",
            escalation_hint="Escalar a supervision humana directa si la conversacion no ocurre.",
        )
        if "interpersonal_conflict" in categories
        else None,
    ]
    blockers = [item for item in blockers if item is not None]
    level = "high" if high_count >= 2 else "medium" if high_count or medium_count else "low"
    process_status = "comprometido" if level == "high" else "en_friccion" if level == "medium" else "en_observacion"
    fatigue_level = "high" if any(item.category == "fatigue" and item.intensity == "high" for item in signals) else "medium" if "fatigue" in categories else "low"
    fatigue = ChangeFatigueAlert(
        level=fatigue_level,
        evidence="Detected fatigue and overload signals." if "fatigue" in categories else "No strong fatigue signal.",
        contributors=[item.summary for item in signals if item.category == "fatigue"],
        confidence=0.8 if "fatigue" in categories else 0.65,
    )
    resistance = ResistanceProfile(
        resistance_type=resistance_type,
        intensity=intensity,
        rationale="Resistance profile derived from repeated friction signals and execution patterns.",
        legitimacy=legitimacy,
        manifestations=manifestations,
        inferred_from_signal_ids=[item.signal_id for item in signals],
        confidence=0.84 if signals else 0.3,
    )
    friction = FrictionAssessment(
        level=level,
        confidence=0.85 if len(signals) >= 2 else 0.65 if signals else 0.3,
        process_status=process_status,
        friction_sources=sorted(categories),
        adoption_maturity="fragile" if level == "high" else "emergent" if level == "medium" else "stable",
        discourse_execution_gap="high" if "execution_block" in categories and "ambiguity" in categories else "medium" if "execution_block" in categories else "low",
        difficult_conversations_pending="interpersonal_conflict" in categories,
    )
    return resistance, blockers, friction, fatigue
