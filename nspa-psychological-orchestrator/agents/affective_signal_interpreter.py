from __future__ import annotations

from domain.affect.models import AffectiveState


NEGATIVE_TERMS = {
    "triste": "sadness",
    "vacio": "emptiness",
    "ansiedad": "anxiety",
    "miedo": "fear",
    "culpa": "guilt",
    "agotado": "exhaustion",
    "solo": "loneliness",
    "bloqueado": "overwhelm",
}

POSITIVE_TERMS = {"mejor": "relief", "tranquilo": "calm", "esperanza": "hope"}


def interpret_affective_signals(text: str) -> dict:
    lowered = text.lower()
    validated = [label for token, label in NEGATIVE_TERMS.items() if token in lowered]
    positive = [label for token, label in POSITIVE_TERMS.items() if token in lowered]
    primary = validated[0] if validated else (positive[0] if positive else "distress")
    intensity = min(1.0, 0.35 + (0.12 * max(len(validated), 1))) if validated else 0.4
    summary = "Malestar emocional presente" if validated else "Estado emocional mixto o no concluyente"
    return {
        "affective_state": AffectiveState(primary_emotion=primary, secondary_emotion=validated[1] if len(validated) > 1 else None, intensity=round(intensity, 2), affective_summary=summary),
        "validated_signals": validated + positive,
    }
