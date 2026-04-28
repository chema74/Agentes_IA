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
    evidence_bundle: list[str] = Field(default_factory=list)
    automation_stop: bool = False
    required_human_owner: str = "lider_del_proceso"
    review_priority: str = "standard"


def evaluate_change_breaker(
    friction: FrictionAssessment,
    resistance: ResistanceProfile,
    blockers: list[AdoptionBlocker],
    fatigue: ChangeFatigueAlert,
) -> CircuitBreakerDecision:
    reasons: list[str] = []
    evidence: list[str] = []
    if friction.confidence < 0.45:
        reasons.append("LOW_DIAGNOSTIC_CONFIDENCE")
        evidence.append(f"Diagnostic confidence too low: {friction.confidence:.2f}")
    if fatigue.level == "high":
        reasons.append("CHANGE_FATIGUE_HIGH")
        evidence.append("Fatiga de cambio alta detectada.")
    if any(item.impact == "critical" for item in blockers):
        reasons.append("PERSISTENT_ADOPTION_BLOCKER")
        evidence.append("Existe al menos un bloqueo de adopcion con impacto critico.")
    if friction.discourse_execution_gap == "high":
        reasons.append("DISCOURSE_EXECUTION_GAP")
        evidence.append("Se observa una brecha fuerte entre discurso y ejecucion.")
    if friction.difficult_conversations_pending:
        reasons.append("DIFFICULT_CONVERSATION_PENDING")
        evidence.append("Hay una conversacion dificil pendiente que condiciona el proceso.")
    if resistance.resistance_type in {"interpersonal_conflict", "overload"} and resistance.intensity == "high":
        reasons.append("HUMAN_INTENSIVE_CASE")
        evidence.append(f"El tipo de resistencia exige manejo humano intensivo: {resistance.resistance_type}.")
    if len(reasons) >= 2 or "LOW_DIAGNOSTIC_CONFIDENCE" in reasons:
        return CircuitBreakerDecision(
            level=4,
            status="circuit_breaker",
            reason_codes=reasons,
            human_review_required=True,
            notes=["La automatizacion debe detenerse y escalar a supervision humana."],
            evidence_bundle=evidence,
            automation_stop=True,
            required_human_owner="responsable_humano",
            review_priority="critical",
        )
    if friction.level == "high":
        return CircuitBreakerDecision(
            level=3,
            status="change_compromised",
            reason_codes=["CHANGE_COMPROMISED"],
            human_review_required=True,
            notes=["El proceso esta comprometido y requiere rediseno o revision humana."],
            evidence_bundle=evidence or ["Convergencia de senales altas de friccion."],
            automation_stop=False,
            required_human_owner="responsable_humano",
            review_priority="high",
        )
    if friction.level == "medium":
        return CircuitBreakerDecision(
            level=2,
            status="relevant_friction",
            human_review_required=False,
            notes=["La friccion es relevante, pero aun intervenible de forma proporcional."],
            evidence_bundle=evidence,
            automation_stop=False,
            required_human_owner="lider_del_proceso",
            review_priority="standard",
        )
    return CircuitBreakerDecision(
        level=1,
        status="observation",
        human_review_required=False,
        notes=["El proceso se mantiene en observacion y seguimiento ligero."],
        evidence_bundle=evidence,
        automation_stop=False,
        required_human_owner="lider_del_proceso",
        review_priority="standard",
    )
