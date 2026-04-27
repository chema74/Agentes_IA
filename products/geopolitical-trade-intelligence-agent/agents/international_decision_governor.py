from __future__ import annotations

from domain.cases.models import DecisionMemorandum, HumanReviewGate


def decide_operational_recommendation(level: int, country: str, confidence: float) -> tuple[str, HumanReviewGate, DecisionMemorandum, list[str]]:
    if level == 4:
        recommendation = "Bloquear automatizacion y escalar a revision humana obligatoria."
    elif level == 3:
        recommendation = "Mantener operacion solo con revision ejecutiva y mitigacion inmediata."
    elif level == 2:
        recommendation = "Reforzar vigilancia comercial y ajustar preventivamente."
    else:
        recommendation = "Mantener observacion de contexto sin cambio operativo inmediato."
    gate = HumanReviewGate(
        status="open" if level >= 3 else "monitoring",
        owner="equipo_ejecutivo" if level >= 3 else "equipo_de_exportacion",
        rationale="Escalado por convergencia de riesgo." if level >= 3 else "Seguimiento reforzado sin bloqueo.",
    )
    memorandum = DecisionMemorandum(summary=f"Memorando ejecutivo para {country}: {recommendation}", confidence=confidence)
    scenarios = [
        "continuidad_controlada" if level <= 2 else "deterioro_relevante",
        "diversificacion_de_ruta" if level >= 2 else "sin_accion_mayor",
    ]
    return recommendation, gate, memorandum, scenarios
