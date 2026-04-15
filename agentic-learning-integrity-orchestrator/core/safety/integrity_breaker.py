from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntegrityAssessment:
    level: int
    label: str
    circuit_breaker_triggered: bool
    notes: list[str]


def evaluate_integrity_level(incoherences: list[str], confidence_score: float, evidence_trace_count: int) -> IntegrityAssessment:
    if confidence_score < 0.35 or evidence_trace_count == 0:
        return IntegrityAssessment(4, "Circuit Breaker", True, ["Evidencia insuficiente para una decision automatica justa."])
    if len(incoherences) >= 3:
        return IntegrityAssessment(3, "Integridad Comprometida", False, ["Convergencia clara de anomalias; requiere revision formal."])
    if len(incoherences) >= 1 or confidence_score < 0.6:
        return IntegrityAssessment(2, "Alerta de Revision", False, ["Senales moderadas de inconsistencia; requiere revision docente."])
    return IntegrityAssessment(1, "Observacion Pedagogica", False, ["No hay senales suficientes para escalar mas alla de seguimiento ligero."])
