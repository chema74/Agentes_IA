from __future__ import annotations

from pydantic import BaseModel, Field

from agents.evaluative_reasoning_engine import build_evaluation_event
from agents.feedback_intervention_planner import build_feedback_plan
from agents.integrity_signal_analyzer import detect_integrity_signals
from agents.learning_evidence_recorder import build_evidence_trace
from agents.teacher_supervision_governor import teacher_supervision_decision
from core.safety.integrity_breaker import evaluate_integrity_level
from domain.feedback.models import FeedbackPlan
from domain.objectives.models import LearningObjective
from services.integrity.alert_builder import build_integrity_alert
from services.langsmith.trace_refs import build_audit_payload
from services.llm.gemini_client import GeminiEvaluatorClient
from services.retrieval.history import summarize_history
from services.storage.repositories import STORE


class OrchestratorInput(BaseModel):
    student_id: str
    objective: LearningObjective
    source_type: str
    activity_type: str
    submission_id: str
    artifact_ref: str
    content: str
    draft_count: int = 1
    time_spent_estimate: float = 1.0


class OrchestratorOutput(BaseModel):
    estado_del_objetivo_de_aprendizaje: str
    resumen_de_traza_de_evidencia: str
    estado_del_evento_de_evaluacion: str
    nivel_de_senal_de_integridad: str
    incoherencias_detectadas: list[str]
    puntuacion_de_confianza: float
    plan_de_retroalimentacion: dict
    intervencion_recomendada: str
    revision_docente_requerida: bool
    estado_de_anulacion_docente: str
    recomendacion_final: str
    referencia_de_auditoria: str


class LearningIntegrityOrchestrator:
    def __init__(self) -> None:
        self.llm = GeminiEvaluatorClient()

    def invoke(self, payload: OrchestratorInput) -> OrchestratorOutput:
        STORE.objectives[payload.objective.id] = payload.objective
        previous_traces = STORE.get_traces(payload.student_id)
        history_summary = summarize_history(previous_traces)
        trace = build_evidence_trace(payload.student_id, payload.objective.id, payload.source_type, payload.activity_type, payload.content, payload.artifact_ref, payload.draft_count, payload.time_spent_estimate)
        STORE.add_trace(payload.student_id, trace)

        incoherences = detect_integrity_signals(history_summary, payload.content, payload.draft_count, payload.time_spent_estimate)
        confidence_score = max(0.15, min(0.95, 0.9 - (0.15 * len(incoherences)) - (0.1 if payload.draft_count <= 1 else 0)))
        process_summary = self.llm.summarize_learning_process(payload.content)
        evaluation = build_evaluation_event(payload.student_id, payload.objective.id, payload.submission_id, payload.objective.rubric_criteria, [trace.id], process_summary, incoherences, confidence_score)
        STORE.evaluations[evaluation.id] = evaluation

        assessment = evaluate_integrity_level(incoherences, confidence_score, len(previous_traces) + 1)
        alert = build_integrity_alert(payload.student_id, evaluation.id, assessment.level, incoherences, confidence_score, assessment.circuit_breaker_triggered)
        if alert is not None:
            STORE.alerts.setdefault(payload.student_id, []).append(alert)

        feedback = build_feedback_plan(evaluation.id, assessment.level, incoherences)
        STORE.feedback_plans[feedback.id] = feedback
        supervision = teacher_supervision_decision(assessment.level, confidence_score)
        audit_ref = build_audit_payload(assessment.level, supervision["recomendacion_final"])

        return OrchestratorOutput(
            estado_del_objetivo_de_aprendizaje="sostenido_por_evidencia" if assessment.level == 1 else "requiere_revision_de_soporte_evidencial",
            resumen_de_traza_de_evidencia=trace.process_summary,
            estado_del_evento_de_evaluacion=evaluation.evaluation_state,
            nivel_de_senal_de_integridad=f"Nivel {assessment.level} - {assessment.label}",
            incoherencias_detectadas=incoherences,
            puntuacion_de_confianza=round(confidence_score, 2),
            plan_de_retroalimentacion=feedback.model_dump(mode="json"),
            intervencion_recomendada=feedback.intervention_type,
            revision_docente_requerida=supervision["revision_docente_requerida"],
            estado_de_anulacion_docente=supervision["estado_de_anulacion_docente"],
            recomendacion_final=supervision["recomendacion_final"],
            referencia_de_auditoria=audit_ref,
        )


ORCHESTRATOR = LearningIntegrityOrchestrator()
