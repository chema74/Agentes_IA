from __future__ import annotations

from pydantic import BaseModel


class InterventionStep(BaseModel):
    step: str
    owner: str
    timing: str


class InterventionPlan(BaseModel):
    focus: str
    steps: list[InterventionStep]
