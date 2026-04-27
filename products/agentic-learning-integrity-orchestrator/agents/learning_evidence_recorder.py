from __future__ import annotations

from uuid import uuid4

from domain.evidence.models import EvidenceTrace


def build_evidence_trace(student_id: str, objective_id: str, source_type: str, activity_type: str, content: str, artifact_ref: str, draft_count: int = 1, time_spent_estimate: float = 1.0) -> EvidenceTrace:
    quality = []
    if len(content.split()) > 80:
        quality.append("respuesta_extensa")
    if any(term in content.lower() for term in ["porque", "ejemplo", "paso"]):
        quality.append("explicacion_argumentada")
    stability = ["proceso_visible"] if draft_count > 1 else ["proceso_limitado"]
    return EvidenceTrace(
        id=f"trace-{uuid4().hex[:12]}",
        student_id=student_id,
        objective_id=objective_id,
        source_type=source_type,
        activity_type=activity_type,
        artifact_ref=artifact_ref,
        draft_count=draft_count,
        revision_markers=["borradores" if draft_count > 1 else "entrega_unica"],
        time_spent_estimate=time_spent_estimate,
        quality_markers=quality,
        stability_markers=stability,
        process_summary="Traza reconstruida a partir de la actividad y metadatos disponibles.",
    )
