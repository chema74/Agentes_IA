from __future__ import annotations

from uuid import uuid4

from domain.evaluation.models import EvaluationEvent


def build_evaluation_event(student_id: str, objective_id: str, submission_id: str, rubric_snapshot: list[str], evidence_refs: list[str], process_summary: str, incoherences: list[str], confidence_score: float) -> EvaluationEvent:
    state = "teacher_review_required" if incoherences or confidence_score < 0.6 else "ready_for_teacher_confirmation"
    return EvaluationEvent(
        id=f"eval-{uuid4().hex[:12]}",
        student_id=student_id,
        objective_id=objective_id,
        submission_id=submission_id,
        rubric_snapshot=rubric_snapshot,
        evidence_refs=evidence_refs,
        performance_summary=process_summary,
        confidence_score=round(confidence_score, 2),
        evaluation_state=state,
        teacher_review_required=state != "ready_for_teacher_confirmation",
    )
