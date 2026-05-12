from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_service_api_key
from app.api.schemas import TradeCasePayload
from core.config.settings import settings
from core.db.session import check_db_health
from services.llm.gemini_client import GEMINI_CLIENT
from services.llm.groq_client import GROQ_CLIENT
from services.orchestration.trade_intelligence_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.storage.repositories import STORE


router = APIRouter(prefix="/api", tags=["geopolitical-trade-intelligence"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "agente-inteligencia-geopolitica",
        "mode": STORE.mode,
        "require_api_key": settings.require_api_key,
        "checks": {"database": check_db_health(), "groq": GROQ_CLIENT.health(), "gemini": GEMINI_CLIENT.health()},
    }


@router.post("/trade-cases/evaluate")
def evaluate(payload: TradeCasePayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.evaluate(
        OrchestratorInput(signal_text=payload.signal_text, country=payload.country, sector=payload.sector, product=payload.product, route=payload.route)
    )
    return result.model_dump(mode="json")


@router.post("/trade-cases/assess-route")
def assess_route(payload: TradeCasePayload, _: str = Depends(require_service_api_key)) -> dict:
    result = ORCHESTRATOR.assess_route(
        OrchestratorInput(signal_text=payload.signal_text, country=payload.country, sector=payload.sector, product=payload.product, route=payload.route)
    )
    return result.model_dump(mode="json")


@router.get("/trade-cases/{case_id}")
def get_case(case_id: str, _: str = Depends(require_service_api_key)) -> dict:
    item = STORE.get_case(case_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Trade case not found")
    return item.model_dump(mode="json")


@router.get("/audit/{reference}")
def get_audit(reference: str, _: str = Depends(require_service_api_key)) -> dict:
    events = STORE.audit_events_by_reference(reference)
    if not events:
        raise HTTPException(status_code=404, detail="Audit reference not found")
    return {"referencia_de_auditoría": reference, "events": [event.model_dump(mode="json") for event in events]}
