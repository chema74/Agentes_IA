from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role
from services.workflows.audit_workflow import WORKFLOW


router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.get("")
def list_evidence(scope_id: str | None = None, current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    evidence_items = list(STORE.evidence.values())
    if scope_id:
        evidence_items = [item for item in evidence_items if item.scope_id == scope_id]
    return [item.model_dump(mode="json") for item in evidence_items]


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    scope_id: str = Form(...),
    source_type: str = Form(default="manual_upload"),
    source_name: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
) -> dict:
    require_role(current_user, "compliance", "auditor", "owner")
    content = await file.read()
    evidence = WORKFLOW.ingest_evidence(
        scope_id=scope_id,
        filename=file.filename or "evidence.bin",
        content=content,
        uploaded_by=current_user.user_id,
        source_type=source_type,
        source_name=source_name or file.filename,
    )
    return evidence.model_dump(mode="json")
