from __future__ import annotations

from dataclasses import dataclass


HIGH_RISK_PATTERNS = {
    "suicide": ["suicid", "quitarme la vida", "matarme", "no quiero vivir", "terminar con todo"],
    "self_harm": ["autolesion", "cortarme", "hacerme dano", "herirme"],
    "abuse": ["me pega", "abuso", "violencia", "agresion"],
    "psychosis": ["escucho voces", "me persiguen", "no se que es real", "todo esta conspirando"],
}


@dataclass
class SafetyAssessment:
    inferred_risk_level: str
    escalation_status: str
    safety_notes: list[str]
    matched_signals: list[str]


def assess_psychological_risk(text: str) -> SafetyAssessment:
    lowered = text.lower()
    matched = []
    for label, patterns in HIGH_RISK_PATTERNS.items():
        if any(pattern in lowered for pattern in patterns):
            matched.append(label)
    if any(item in {"suicide", "self_harm", "psychosis"} for item in matched):
        return SafetyAssessment(
            inferred_risk_level="high",
            escalation_status="HIGH_RISK_ESCALATION",
            safety_notes=[
                "Suspender apoyo ordinario y priorizar orientacion inmediata a ayuda humana.",
                "No explorar en abierto si hay riesgo inmediato.",
            ],
            matched_signals=matched,
        )
    if matched:
        return SafetyAssessment(
            inferred_risk_level="medium",
            escalation_status="ELEVATED_MONITORING",
            safety_notes=["Mantener contencion, validar experiencia y recomendar apoyo humano cercano."],
            matched_signals=matched,
        )
    return SafetyAssessment(
        inferred_risk_level="low",
        escalation_status="NORMAL_SUPPORT",
        safety_notes=["Sin senales de crisis inmediata en el mensaje actual."],
        matched_signals=[],
    )
