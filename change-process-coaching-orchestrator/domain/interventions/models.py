from __future__ import annotations

from pydantic import BaseModel, Field


class InterventionStep(BaseModel):
    step: str
    owner: str
    timing: str
    intervention_type: str = "clarification"
    objective: str = ""
    success_metric: str = ""


class InterventionPlan(BaseModel):
    focus: str
    intervention_mode: str = "proportional"
    sequencing_rationale: str = ""
    escalation_conditions: list[str] = Field(default_factory=list)
    steps: list[InterventionStep]
