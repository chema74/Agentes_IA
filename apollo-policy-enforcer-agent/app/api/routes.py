from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import EnforcementPayload
from services.orchestration.policy_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.policies.policy_repository import POLICY_REPOSITORY
from services.storage.repositories import STORE


router = APIRouter(prefix="/api", tags=["apollo-policy"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "apollo-policy-enforcer-agent", "mode": STORE.mode}


@router.post("/enforce")
def enforce(payload: EnforcementPayload) -> dict:
    result = ORCHESTRATOR.enforce(
        OrchestratorInput(
            request_text=payload.request_text,
            actor_id=payload.actor_id,
            target_resource=payload.target_resource,
            context=payload.context,
        )
    )
    return result.model_dump(mode="json")


@router.post("/validate")
def validate(payload: EnforcementPayload) -> dict:
    result = ORCHESTRATOR.validate(
        OrchestratorInput(
            request_text=payload.request_text,
            actor_id=payload.actor_id,
            target_resource=payload.target_resource,
            context=payload.context,
        )
    )
    return result.model_dump(mode="json")


@router.get("/mandates/{mandate_id}")
def get_mandate(mandate_id: str) -> dict:
    mandate = STORE.mandates.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="Mandate not found")
    return mandate.model_dump(mode="json")


@router.get("/audit/{reference}")
def get_audit(reference: str) -> dict:
    events = STORE.audit_events_by_reference(reference)
    if not events:
        raise HTTPException(status_code=404, detail="Audit reference not found")
    return {"audit_reference": reference, "events": [event.model_dump(mode="json") for event in events]}


@router.get("/policies/{policy_id}")
def get_policy(policy_id: str) -> dict:
    policy = POLICY_REPOSITORY.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy.model_dump(mode="json")
