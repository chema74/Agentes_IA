from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.deps import require_service_api_key
from app.api.schemas import EnforcementPayload
from core.config.settings import settings
from core.db.session import check_db_health
from services.llm.sambanova_client import SAMBANOVA_CLIENT
from services.orchestration.policy_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.policies.policy_repository import POLICY_REPOSITORY
from services.state.state_repository import STATE_REPOSITORY
from services.storage.repositories import STORE


router = APIRouter(prefix="/api", tags=["apollo-policy"])


@router.get("/health")
def health() -> dict:
    checks = {
        "database": check_db_health(),
        "policy_backend": POLICY_REPOSITORY.health(),
        "state_backend": STATE_REPOSITORY.health(),
        "llm": SAMBANOVA_CLIENT.health(),
    }
    overall = "ok"
    if any(item["status"] == "error" for item in checks.values()):
        overall = "degraded"
    return {
        "status": overall,
        "service": "agente-cumplimiento-politicas",
        "mode": STORE.mode,
        "require_api_key": settings.require_api_key,
        "checks": checks,
    }


@router.post("/enforce")
def enforce(
    payload: EnforcementPayload,
    _: str = Depends(require_service_api_key),
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
) -> dict:
    result = ORCHESTRATOR.enforce(
        OrchestratorInput(
            request_text=payload.request_text,
            actor_id=payload.actor_id,
            target_resource=payload.target_resource,
            context=payload.context,
            request_id=payload.request_id or x_request_id,
            idempotency_key=x_idempotency_key,
        )
    )
    return result.model_dump(mode="json")


@router.post("/validate")
def validate(
    payload: EnforcementPayload,
    _: str = Depends(require_service_api_key),
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
) -> dict:
    result = ORCHESTRATOR.validate(
        OrchestratorInput(
            request_text=payload.request_text,
            actor_id=payload.actor_id,
            target_resource=payload.target_resource,
            context=payload.context,
            request_id=payload.request_id or x_request_id,
        )
    )
    return result.model_dump(mode="json")


@router.get("/mandates/{mandate_id}")
def get_mandate(mandate_id: str, _: str = Depends(require_service_api_key)) -> dict:
    mandate = STORE.get_mandate(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="Mandate not found")
    return mandate.model_dump(mode="json")


@router.get("/audit/{reference}")
def get_audit(reference: str, _: str = Depends(require_service_api_key)) -> dict:
    events = STORE.audit_events_by_reference(reference)
    if not events:
        raise HTTPException(status_code=404, detail="Audit reference not found")
    return {"audit_reference": reference, "events": [event.model_dump(mode="json") for event in events]}


@router.get("/policies/{policy_id}")
def get_policy(policy_id: str, _: str = Depends(require_service_api_key)) -> dict:
    policy = POLICY_REPOSITORY.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy.model_dump(mode="json")
