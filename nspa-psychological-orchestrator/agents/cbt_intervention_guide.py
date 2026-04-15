from __future__ import annotations

from domain.interventions.models import CBTIntervention


def select_cbt_intervention(risk_level: str, primary_emotion: str, continuity_notes: str) -> CBTIntervention:
    if risk_level == "high":
        return CBTIntervention(
            intervention_style="crisis_containment",
            rationale="La prioridad es seguridad y contacto con ayuda humana inmediata.",
            prompt_frame="Validar, orientar a emergencia, reducir exploracion y pedir accion concreta inmediata.",
            recommended_next_step="Contactar ahora con un recurso humano urgente o servicio de emergencia de tu zona.",
        )
    if primary_emotion in {"anxiety", "fear", "overwhelm"}:
        return CBTIntervention(
            intervention_style="grounding_and_cognitive_defusion",
            rationale="El estado actual sugiere activacion elevada y posible fusion con pensamientos amenazantes.",
            prompt_frame="Validar activacion, acotar el foco y proponer una accion reguladora concreta.",
            recommended_next_step="Hacer una pausa breve, nombrar tres hechos presentes y elegir una accion pequena y verificable en la proxima hora.",
        )
    return CBTIntervention(
        intervention_style="validation_and_reframing",
        rationale="Conviene contener, ordenar la narrativa y reducir conclusiones absolutas.",
        prompt_frame="Validar dolor, separar hecho de interpretacion y recuperar continuidad narrativa.",
        recommended_next_step="Escribir una version breve de lo que esta pasando diferenciando hechos, interpretaciones y necesidad inmediata.",
    )
