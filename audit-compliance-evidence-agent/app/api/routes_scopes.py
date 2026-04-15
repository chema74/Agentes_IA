from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role
from domain.scopes.models import AuditScope
from services.workflows.audit_workflow import WORKFLOW


router = APIRouter(prefix="/api/scopes", tags=["scopes"])


class ScopeCreateRequest(BaseModel):
    id: str
    name: str
    description: str = ""
    framework: str = ""
    status: str = "draft"


@router.get("")
def list_scopes(current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    return [scope.model_dump(mode="json") for scope in STORE.scopes.values()]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_scope(payload: ScopeCreateRequest, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    if payload.id in STORE.scopes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El scope ya existe.")
    scope = AuditScope(
        id=payload.id,
        name=payload.name,
        description=payload.description,
        framework=payload.framework,
        status=payload.status,
        created_by=current_user.user_id,
    )
    return WORKFLOW.create_scope(scope).model_dump(mode="json")
