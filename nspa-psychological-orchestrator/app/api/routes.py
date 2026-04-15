from __future__ import annotations

try:
    from fastapi import APIRouter
except ImportError:
    APIRouter = None

from app.api.schemas import MessageRequest, OrchestratorResponse
from services.orchestration.psychological_orchestrator import ORCHESTRATOR, OrchestratorInput


router = APIRouter(prefix="/api", tags=["orchestrator"]) if APIRouter else None

if router is not None:
    @router.get("/health")
    def health() -> dict:
        return {"status": "ok", "service": "nspa-psychological-orchestrator"}

    @router.post("/support", response_model=OrchestratorResponse)
    def support(payload: MessageRequest) -> OrchestratorResponse:
        result = ORCHESTRATOR.invoke(OrchestratorInput(user_id=payload.user_id, message=payload.message))
        return OrchestratorResponse(**result.model_dump(mode="json"))
