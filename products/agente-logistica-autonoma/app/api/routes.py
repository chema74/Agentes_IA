from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import EvaluateDisruptionPayload, ExecuteRecoveryPayload
from services.orchestration.logistics_orchestrator import ORCHESTRATOR, OrchestratorInput
from services.storage.repositories import STORE


router = APIRouter(prefix="/api", tags=["a2a-logistics"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "agente-logistica-autonoma", "mode": STORE.mode}


@router.post("/disruptions/evaluate")
def evaluate_disruption(payload: EvaluateDisruptionPayload) -> dict:
    result = ORCHESTRATOR.evaluate(OrchestratorInput(task=payload.task, disruption=payload.disruption))
    return result.model_dump(mode="json")


@router.post("/recovery/execute")
def execute_recovery(payload: ExecuteRecoveryPayload) -> dict:
    result = ORCHESTRATOR.execute(
        OrchestratorInput(task=payload.task, disruption=payload.disruption, recovery_plan_id=payload.recovery_plan_id)
    )
    return result.model_dump(mode="json")


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict:
    task = STORE.tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump(mode="json")


@router.get("/recovery-plans/{plan_id}")
def get_recovery_plan(plan_id: str) -> dict:
    plan = STORE.recovery_plans.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    return plan.model_dump(mode="json")


@router.get("/audit/{reference}")
def get_audit(reference: str) -> dict:
    events = STORE.audit_events_by_reference(reference)
    if not events:
        raise HTTPException(status_code=404, detail="Audit reference not found")
    return {"audit_reference": reference, "events": [event.model_dump(mode="json") for event in events]}
