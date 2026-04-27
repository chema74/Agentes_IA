from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_service_api_key
from app.api.schemas import NegotiatePayload, ReviewPayload
from core.config.settings import settings
from core.db.session import check_db_health
from services.llm.gemini_client import GEMINI_CLIENT
from services.orchestration.legal_counsel_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.storage.repositories import STORE


router = APIRouter(prefix="/api", tags=["autonomous-legal-counsel"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "autonomous-legal-counsel-agent",
        "mode": STORE.mode,
        "require_api_key": settings.require_api_key,
        "checks": {"database": check_db_health(), "llm": GEMINI_CLIENT.health()},
    }


@router.post("/contracts/review")
def review_contract(payload: ReviewPayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.review(OrchestratorInput(contract_text=payload.contract_text, counterparty_name=payload.counterparty_name))
    return result.model_dump(mode="json")


@router.post("/contracts/redline")
def redline_contract(payload: ReviewPayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.redline(OrchestratorInput(contract_text=payload.contract_text, counterparty_name=payload.counterparty_name))
    return result.model_dump(mode="json")


@router.post("/contracts/negotiate")
def negotiate_contract(payload: NegotiatePayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.negotiate(
        OrchestratorInput(
            contract_text=payload.contract_text,
            counterparty_name=payload.counterparty_name,
            issue_key=payload.issue_key,
            counterparty_response=payload.counterparty_response,
        )
    )
    return result.model_dump(mode="json")


@router.get("/reviews/{review_id}")
def get_review(review_id: str, _: str = Depends(require_service_api_key)) -> dict:
    review = STORE.get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.model_dump(mode="json")


@router.get("/audit/{reference}")
def get_audit(reference: str, _: str = Depends(require_service_api_key)) -> dict:
    events = STORE.audit_events_by_reference(reference)
    if not events:
        raise HTTPException(status_code=404, detail="Audit reference not found")
    return {"audit_reference": reference, "events": [event.model_dump(mode="json") for event in events]}
