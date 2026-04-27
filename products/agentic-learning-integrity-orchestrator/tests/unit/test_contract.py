from __future__ import annotations

from domain.objectives.models import LearningObjective
from services.orchestration.learning_integrity_orchestrator import ORCHESTRATOR, OrchestratorInput


def build_objective() -> LearningObjective:
    return LearningObjective(
        id="obj-001",
        course_id="course-001",
        title="Argumentacion escrita",
        description="Demostrar comprension y justificacion de una postura academica.",
        rubric_criteria=["Claridad conceptual", "Uso de evidencia", "Proceso visible"],
        expected_evidence_patterns=["borradores", "revision", "justificacion"],
        difficulty_level="medium",
    )


def test_output_contract_contains_required_fields():
    result = ORCHESTRATOR.invoke(OrchestratorInput(student_id="stu-001", objective=build_objective(), source_type="lms", activity_type="essay", submission_id="sub-001", artifact_ref="artifact-001", content="He hecho una primera version con dudas y varias correcciones.", draft_count=2, time_spent_estimate=1.2))
    payload = result.model_dump(mode="json")
    for key in [
        "estado_del_objetivo_de_aprendizaje",
        "resumen_de_traza_de_evidencia",
        "estado_del_evento_de_evaluacion",
        "nivel_de_senal_de_integridad",
        "incoherencias_detectadas",
        "puntuacion_de_confianza",
        "plan_de_retroalimentacion",
        "intervencion_recomendada",
        "revision_docente_requerida",
        "estado_de_anulacion_docente",
        "recomendacion_final",
        "referencia_de_auditoria",
    ]:
        assert key in payload
