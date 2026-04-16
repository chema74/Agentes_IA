from __future__ import annotations

from domain.friction.models import FrictionAssessment
from domain.progress.models import HumanSupervisionGate, TransformationMilestone
from domain.resistance.models import ResistanceProfile


def supervision_decision(friction: FrictionAssessment, resistance: ResistanceProfile, breaker_level: int) -> tuple[HumanSupervisionGate, list[TransformationMilestone], dict]:
    gate = HumanSupervisionGate(
        status="open" if breaker_level >= 3 else "monitoring",
        owner="responsable_humano" if breaker_level >= 3 else "lider_del_proceso",
        rationale="Escalate to human supervision." if breaker_level >= 3 else "Keep human oversight with light monitoring.",
        next_review_action="Revision humana prioritaria del caso." if breaker_level >= 3 else "Seguimiento ligero con foco en senales nuevas.",
        automation_allowed=breaker_level < 4,
    )
    milestones = [
        TransformationMilestone(
            milestone="claridad_del_cambio",
            status="pendiente" if friction.level != "low" else "estable",
            evidence="El proceso requiere una narrativa compartida del cambio." if friction.level != "low" else "Existe claridad operativa suficiente.",
        ),
        TransformationMilestone(
            milestone="sostenibilidad_del_cambio",
            status="en_riesgo" if resistance.intensity == "high" else "en_progreso",
            evidence="La intensidad de la resistencia compromete la consolidacion." if resistance.intensity == "high" else "El cambio mantiene traccion razonable.",
        ),
    ]
    recommendation = {
        "summary": "Escalado humano prioritario." if breaker_level >= 4 else "Intervencion proporcional y seguimiento." if breaker_level >= 2 else "Seguimiento ligero.",
        "level": breaker_level,
        "rationale": "La proporcionalidad final depende del nivel de friccion, la resistencia y el breaker.",
        "automation_mode": "stopped" if breaker_level >= 4 else "human_review" if breaker_level >= 3 else "monitored",
        "next_best_owner": "responsable_humano" if breaker_level >= 3 else "lider_del_proceso",
    }
    return gate, milestones, recommendation
