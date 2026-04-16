from __future__ import annotations

from domain.friction.models import FrictionAssessment
from domain.progress.models import HumanSupervisionGate, TransformationMilestone
from domain.resistance.models import ResistanceProfile


def supervision_decision(friction: FrictionAssessment, resistance: ResistanceProfile, breaker_level: int) -> tuple[HumanSupervisionGate, list[TransformationMilestone], dict]:
    gate = HumanSupervisionGate(
        status="open" if breaker_level >= 3 else "monitoring",
        owner="responsable_humano" if breaker_level >= 3 else "lider_del_proceso",
        rationale="Escalate to human supervision." if breaker_level >= 3 else "Keep human oversight with light monitoring.",
    )
    milestones = [
        TransformationMilestone(milestone="claridad_de_objetivo", status="pendiente" if friction.level != "low" else "estable"),
        TransformationMilestone(milestone="sostenibilidad_del_cambio", status="en_riesgo" if resistance.intensity == "high" else "en_progreso"),
    ]
    recommendation = {
        "summary": "Escalado humano prioritario." if breaker_level >= 4 else "Intervencion proporcional y seguimiento." if breaker_level >= 2 else "Seguimiento ligero.",
        "level": breaker_level,
    }
    return gate, milestones, recommendation
