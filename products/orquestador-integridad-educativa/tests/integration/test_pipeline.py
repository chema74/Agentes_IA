from __future__ import annotations

from domain.objectives.models import LearningObjective
from services.orchestration.learning_integrity_orchestrator import ORCHESTRATOR, OrchestratorInput


def objective() -> LearningObjective:
    return LearningObjective(
        id="obj-002",
        course_id="course-001",
        title="Resolucion razonada",
        description="Explicar decisiones y procedimiento de una tarea academica.",
        rubric_criteria=["Proceso", "Consistencia", "Transferencia"],
        expected_evidence_patterns=["iteraciones", "explicacion", "revision"],
        difficulty_level="high",
    )


def test_integration_flags_revision_for_low_process_submission():
    result = ORCHESTRATOR.invoke(OrchestratorInput(student_id="stu-low", objective=objective(), source_type="lms", activity_type="assignment", submission_id="sub-low", artifact_ref="artifact-low", content="Respuesta final sin cambios y optimizacion total.", draft_count=1, time_spent_estimate=0.1))
    assert result.revision_docente_requerida is True
    assert "Nivel" in result.nivel_de_senal_de_integridad
