from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_service_api_key
from app.api.schemas import ChangeCasePayload
from core.config.settings import settings
from services.llm.gemini_client import GEMINI_CLIENT
from services.llm.groq_client import GROQ_CLIENT
from services.orchestration.change_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.storage.repositories import STORE


router = APIRouter(prefix="/api", tags=["change-process-coaching"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "orquestador-coaching-cambio",
        "mode": STORE.mode,
        "require_api_key": settings.require_api_key,
        "checks": {"storage": STORE.health_report(), "groq": GROQ_CLIENT.health(), "gemini": GEMINI_CLIENT.health()},
    }


@router.post("/change-cases/evaluate")
def evaluate(payload: ChangeCasePayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.evaluate(
        OrchestratorInput(
            process_notes=payload.process_notes,
            context_type=payload.context_type,
            change_goal=payload.change_goal,
            change_phase=payload.change_phase,
            requested_mode=payload.requested_mode,
            case_id=payload.case_id,
            signals=payload.signals,
            stakeholders=payload.stakeholders,
            sessions=payload.sessions,
            tasks=payload.tasks,
            survey_inputs=payload.survey_inputs,
            source_systems=payload.source_systems,
        )
    )
    return result.model_dump(mode="json", by_alias=True)


@router.post("/change-cases/intervene")
def intervene(payload: ChangeCasePayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.intervene(
        OrchestratorInput(
            process_notes=payload.process_notes,
            context_type=payload.context_type,
            change_goal=payload.change_goal,
            change_phase=payload.change_phase,
            requested_mode=payload.requested_mode,
            case_id=payload.case_id,
            signals=payload.signals,
            stakeholders=payload.stakeholders,
            sessions=payload.sessions,
            tasks=payload.tasks,
            survey_inputs=payload.survey_inputs,
            source_systems=payload.source_systems,
        )
    )
    return result.model_dump(mode="json", by_alias=True)


@router.get("/change-cases/{case_id}")
def get_case(case_id: str, _: str = Depends(require_service_api_key)) -> dict:
    item = STORE.get_case(case_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Change case not found")
    return item.model_dump(mode="json", by_alias=True)


@router.get("/audit/{reference}")
def get_audit(reference: str, _: str = Depends(require_service_api_key)) -> dict:
    events = STORE.audit_events_by_reference(reference)
    if not events:
        raise HTTPException(status_code=404, detail="Audit reference not found")
    return {"referencia_de_auditor\u00eda": reference, "events": [event.model_dump(mode="json") for event in events]}
