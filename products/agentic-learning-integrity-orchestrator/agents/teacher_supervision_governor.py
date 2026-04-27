from __future__ import annotations


def teacher_supervision_decision(level: int, confidence_score: float) -> dict:
    review_required = level >= 2 or confidence_score < 0.75
    return {
        "revision_docente_requerida": review_required,
        "estado_de_anulacion_docente": "pendiente" if review_required else "no_aplica",
        "recomendacion_final": "revision_docente_obligatoria" if level >= 3 else ("revision_docente_recomendada" if review_required else "retroalimentacion_y_seguimiento"),
    }
