from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role
from services.workflows.audit_workflow import WORKFLOW


router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.get("")
def list_packages(scope_id: str | None = None, current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    packages = list(STORE.packages.values())
    if scope_id:
        packages = [item for item in packages if item.scope_id == scope_id]
    return [item.model_dump(mode="json") for item in packages]


@router.post("/export/{scope_id}")
def export_package(scope_id: str, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    if scope_id not in STORE.scopes:
        raise HTTPException(status_code=404, detail="Scope no encontrado.")
    package = WORKFLOW.export_package(scope_id, created_by=current_user.user_id)
    return package.model_dump(mode="json")
