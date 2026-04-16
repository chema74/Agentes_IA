from __future__ import annotations

from domain.friction.models import AdoptionBlocker, FrictionAssessment
from domain.interventions.models import InterventionPlan, InterventionStep
from domain.resistance.models import ResistanceProfile


def build_intervention_plan(friction: FrictionAssessment, resistance: ResistanceProfile, blockers: list[AdoptionBlocker]) -> InterventionPlan:
    steps = [
        InterventionStep(step="Explicitar que esta cambiando y en que secuencia.", owner="responsable_del_cambio", timing="48h"),
    ]
    if blockers:
        steps.append(InterventionStep(step="Resolver bloqueo operativo prioritario.", owner="lider_de_area", timing="72h"))
    if resistance.resistance_type == "interpersonal_conflict":
        steps.append(InterventionStep(step="Abrir conversacion dificil con facilitacion humana.", owner="responsable_humano", timing="inmediato"))
    elif friction.level == "medium":
        steps.append(InterventionStep(step="Refuerzo de seguimiento y expectativas.", owner="lider", timing="1 semana"))
    return InterventionPlan(focus="proportional_change_intervention", steps=steps)
