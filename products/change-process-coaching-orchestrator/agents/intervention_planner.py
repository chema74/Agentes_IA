from __future__ import annotations

from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.interventions.models import InterventionPlan, InterventionStep
from domain.resistance.models import ResistanceProfile


def build_intervention_plan(friction: FrictionAssessment, resistance: ResistanceProfile, blockers: list[AdoptionBlocker]) -> InterventionPlan:
    steps = [
        InterventionStep(
            step="Explicitar que esta cambiando, por que, con que impacto y en que secuencia.",
            owner="responsable_del_cambio",
            timing="48h",
            intervention_type="clarification",
            objective="Reducir ambiguedad y alinear expectativas inmediatas.",
            success_metric="Existe una narrativa comun del cambio y responsables claros para la siguiente semana.",
        ),
    ]
    if blockers:
        steps.append(
            InterventionStep(
                step="Resolver el bloqueo de adopcion prioritario antes de introducir nuevas exigencias.",
                owner="lider_de_area",
                timing="72h",
                intervention_type="blocker_removal",
                objective="Recuperar continuidad de ejecucion.",
                success_metric="El bloqueo critico deja de impedir la secuencia definida.",
            )
        )
    if resistance.resistance_type == "interpersonal_conflict":
        steps.append(
            InterventionStep(
                step="Abrir una conversacion dificil con facilitacion humana y reglas de seguridad relacional.",
                owner="responsable_humano",
                timing="inmediato",
                intervention_type="facilitated_conversation",
                objective="Desbloquear conflicto relacional que compromete el cambio.",
                success_metric="La conversacion ocurre y deja acuerdos verificables o un desacuerdo explicitado.",
            )
        )
    elif friction.level == "medium":
        steps.append(
            InterventionStep(
                step="Reforzar seguimiento, expectativas y capacidad de absorcion sin aumentar presion indiscriminada.",
                owner="lider",
                timing="1 semana",
                intervention_type="follow_up",
                objective="Sostener el progreso sin disparar fatiga de cambio.",
                success_metric="Las proximas acciones se completan con menor friccion y sin nuevas senales altas.",
            )
        )
    return InterventionPlan(
        focus="proportional_change_intervention",
        intervention_mode="human_guided" if resistance.intensity == "high" else "proportional",
        sequencing_rationale="Primero claridad y bloqueo principal, despues acompanamiento y consolidacion.",
        escalation_conditions=[
            "Persistencia de fatiga alta",
            "Incoherencia fuerte entre discurso y ejecucion",
            "Conversacion dificil no realizada",
        ],
        steps=steps,
    )
