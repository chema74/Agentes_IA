from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import SupportPayload
from domain.objectives.models import LearningObjective
from services.orchestration.learning_integrity_orchestrator import ORCHESTRATOR, OrchestratorInput


router = APIRouter(prefix="/api", tags=["learning-integrity"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "agentic-learning-integrity-orchestrator"}


@router.post("/evaluate")
def evaluate(payload: SupportPayload) -> dict:
    objective = LearningObjective(**payload.objective.model_dump())
    result = ORCHESTRATOR.invoke(
        OrchestratorInput(
            student_id=payload.student_id,
            objective=objective,
            source_type=payload.source_type,
            activity_type=payload.activity_type,
            submission_id=payload.submission_id,
            artifact_ref=payload.artifact_ref,
            content=payload.content,
            draft_count=payload.draft_count,
            time_spent_estimate=payload.time_spent_estimate,
        )
    )
    return result.model_dump(mode="json")
