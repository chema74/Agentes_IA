from __future__ import annotations


def detect_integrity_signals(history_summary: str, current_submission: str, draft_count: int, time_spent_estimate: float) -> list[str]:
    signals = []
    lowered = current_submission.lower()
    if draft_count <= 1:
        signals.append("ausencia_de_proceso_intermedio")
    if time_spent_estimate < 0.2:
        signals.append("tiempo_inusualmente_bajo")
    if "como modelo de lenguaje" in lowered or "ia" in lowered:
        signals.append("referencia_explicita_a_generacion_asistida")
    if history_summary and len(current_submission.split()) > 2 * max(len(history_summary.split()), 1):
        signals.append("salto_brusco_de_complejidad")
    if any(term in lowered for term in ["optimizacion total", "respuesta perfecta", "texto final sin cambios"]):
        signals.append("producto_excesivamente_optimizado")
    return signals
