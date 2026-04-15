from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role
from domain.remediation.models import Remediation
from services.workflows.audit_workflow import WORKFLOW


router = APIRouter(prefix="/api/remediations", tags=["remediations"])


class RemediationCreateRequest(BaseModel):
    id: str
    scope_id: str
    finding_id: str
    title: str
    description: str
    status: str = "proposed"
    owner_user_id: str | None = None
    target_date: str | None = None
    completion_note: str | None = None


@router.get("")
def list_remediations(scope_id: str | None = None, current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    remediations = list(STORE.remediations.values())
    if scope_id:
        remediations = [item for item in remediations if item.scope_id == scope_id]
    return [item.model_dump(mode="json") for item in remediations]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_remediation(payload: RemediationCreateRequest, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor", "owner")
    if payload.finding_id not in STORE.findings:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado.")
    remediation = Remediation(**payload.model_dump())
    return WORKFLOW.create_remediation(remediation, actor_user_id=current_user.user_id).model_dump(mode="json")
