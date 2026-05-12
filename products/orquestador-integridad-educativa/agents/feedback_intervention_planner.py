from __future__ import annotations

from uuid import uuid4

from domain.feedback.models import FeedbackPlan


def build_feedback_plan(evaluation_event_id: str, integrity_level: int, incoherences: list[str]) -> FeedbackPlan:
    if integrity_level >= 4:
        return FeedbackPlan(
            id=f"fb-{uuid4().hex[:12]}",
            evaluation_event_id=evaluation_event_id,
            feedback_summary="No se recomienda cierre evaluativo automatico. Hace falta reconstruir proceso y revisar con el docente.",
            intervention_type="reevaluacion_guiada",
            recommended_actions=["Solicitar explicacion oral o escrita del proceso.", "Pedir borrador o evidencia adicional.", "Abrir revision docente formal."],
            teacher_notes_required=True,
            followup_window="inmediato",
        )
    if integrity_level == 2 or integrity_level == 3:
        return FeedbackPlan(
            id=f"fb-{uuid4().hex[:12]}",
            evaluation_event_id=evaluation_event_id,
            feedback_summary="Conviene revisar la coherencia entre producto final y proceso antes de consolidar la evaluacion.",
            intervention_type="seguimiento_docente",
            recommended_actions=["Revisar trazas y borradores.", "Preguntar por decisiones clave del trabajo.", "Ajustar la evaluacion si el proceso no sostiene el resultado."],
            teacher_notes_required=True,
            followup_window="48h",
        )
    return FeedbackPlan(
        id=f"fb-{uuid4().hex[:12]}",
        evaluation_event_id=evaluation_event_id,
        feedback_summary="La evidencia sostiene el aprendizaje con necesidad de mejora puntual.",
        intervention_type="retroalimentacion_formativa",
        recommended_actions=["Ofrecer comentario especifico sobre el criterio mas debil.", "Sugerir una practica de transferencia corta."],
        teacher_notes_required=False,
        followup_window="proxima_entrega",
    )
