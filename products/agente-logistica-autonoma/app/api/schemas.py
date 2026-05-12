from __future__ import annotations

from pydantic import BaseModel

from domain.tasks.models import DisruptionEvent, LogisticsTask


class EvaluateDisruptionPayload(BaseModel):
    task: LogisticsTask
    disruption: DisruptionEvent


class ExecuteRecoveryPayload(BaseModel):
    task: LogisticsTask
    disruption: DisruptionEvent
    recovery_plan_id: str | None = None
