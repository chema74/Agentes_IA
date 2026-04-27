from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role
from domain.controls.models import Control
from services.workflows.audit_workflow import WORKFLOW


router = APIRouter(prefix="/api/controls", tags=["controls"])


class ControlCreateRequest(BaseModel):
    id: str
    scope_id: str
    code: str
    name: str
    description: str
    category: str
    criticality: str
    expected_criterion: str
    status: str = "draft"
    owner_user_id: str | None = None
    version: str = "1.0"


@router.get("")
def list_controls(scope_id: str | None = None, current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    controls = list(STORE.controls.values())
    if scope_id:
        controls = [control for control in controls if control.scope_id == scope_id]
    return [control.model_dump(mode="json") for control in controls]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_control(payload: ControlCreateRequest, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    if payload.id in STORE.controls:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El control ya existe.")
    control = Control(**payload.model_dump())
    return WORKFLOW.create_control(control, actor_user_id=current_user.user_id).model_dump(mode="json")


@router.post("/import")
async def import_controls(scope_id: str, file: UploadFile = File(...), current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    content = (await file.read()).decode("utf-8", errors="ignore")
    reader = csv.DictReader(StringIO(content))
    imported = []
    for index, row in enumerate(reader, start=1):
        control_id = row.get("id") or f"{scope_id}-control-{index}"
        control = Control(
            id=control_id,
            scope_id=scope_id,
            code=row.get("code", control_id),
            name=row.get("name", "Control sin nombre"),
            description=row.get("description", ""),
            category=row.get("category", "general"),
            criticality=row.get("criticality", "medium"),
            expected_criterion=row.get("expected_criterion", ""),
            status=row.get("status", "draft"),
            owner_user_id=row.get("owner_user_id") or None,
            version=row.get("version", "1.0"),
        )
        WORKFLOW.create_control(control, actor_user_id=current_user.user_id)
        imported.append(control.model_dump(mode="json"))
    return {"imported": imported, "count": len(imported)}
