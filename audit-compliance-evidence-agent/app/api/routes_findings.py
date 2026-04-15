from __future__ import annotations

from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from core.db.repository import STORE
from core.security.access import require_role


router = APIRouter(prefix="/api/findings", tags=["findings"])


class FindingReviewRequest(BaseModel):
    status: str


@router.get("")
def list_findings(scope_id: str | None = None, current_user=Depends(get_current_user)) -> list[dict]:
    require_role(current_user, "compliance", "auditor", "owner")
    findings = list(STORE.findings.values())
    if scope_id:
        findings = [item for item in findings if item.scope_id == scope_id]
    return [item.model_dump(mode="json") for item in findings]


@router.post("/review/{finding_id}")
def review_finding(finding_id: str, payload: FindingReviewRequest, current_user=Depends(get_current_user)) -> dict:
    require_role(current_user, "compliance", "auditor")
    finding = STORE.findings.get(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado.")
    if finding.severity in {"high", "critical"} and payload.status == "closed":
        raise HTTPException(status_code=400, detail="Los hallazgos altos o criticos no se cierran sin validacion humana fuera del sistema.")
    finding.status = payload.status
    finding.updated_at = datetime.now(UTC)
    return finding.model_dump(mode="json")
