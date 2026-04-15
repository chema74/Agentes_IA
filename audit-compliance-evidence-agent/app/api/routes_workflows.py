from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role
from services.workflows.audit_workflow import WORKFLOW


router = APIRouter(prefix="/api", tags=["workflow"])


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "service": "audit-compliance-evidence-agent"}


@router.get("/mappings")
def list_mappings(scope_id: str | None = None, current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    mappings = list(STORE.mappings.values())
    if scope_id:
        control_ids = {control.id for control in STORE.controls.values() if control.scope_id == scope_id}
        mappings = [mapping for mapping in mappings if mapping.control_id in control_ids]
    return [mapping.model_dump(mode="json") for mapping in mappings]


@router.post("/mappings/suggest/{scope_id}")
def suggest_mappings(scope_id: str, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    if scope_id not in STORE.scopes:
        raise HTTPException(status_code=404, detail="Scope no encontrado.")
    mappings = WORKFLOW.suggest_mappings_for_scope(scope_id)
    return {"count": len(mappings), "items": [mapping.model_dump(mode="json") for mapping in mappings]}


@router.post("/mappings/review/{mapping_id}")
def review_mapping(mapping_id: str, approved: bool, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    if mapping_id not in STORE.mappings:
        raise HTTPException(status_code=404, detail="Mapping no encontrado.")
    WORKFLOW.review_mapping(mapping_id, reviewed_by=current_user.user_id, approved=approved)
    return STORE.mappings[mapping_id].model_dump(mode="json")


@router.post("/evaluations/run/{scope_id}")
def run_scope_evaluation(scope_id: str, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    if scope_id not in STORE.scopes:
        raise HTTPException(status_code=404, detail="Scope no encontrado.")
    result = WORKFLOW.evaluate_scope(scope_id)
    return {
        "coverage": [item.model_dump(mode="json") for item in result["coverage"]],
        "gaps": [item.model_dump(mode="json") for item in result["gaps"]],
        "findings": [item.model_dump(mode="json") for item in result["findings"]],
    }
