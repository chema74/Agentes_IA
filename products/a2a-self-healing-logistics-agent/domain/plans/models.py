from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class RecoveryOption(BaseModel):
    option_id: str
    agent_id: str
    execution_mode: str
    incremental_cost: float
    projected_total_delay_minutes: int
    projected_sla_breach_minutes: int
    activation_minutes: int
    reliability_score: float
    regulatory_compliant: bool = True
    operationally_feasible: bool = True
    confidence_score: float
    tradeoffs: list[str] = Field(default_factory=list)
    missing_critical_data: bool = False
    requires_human_approval: bool = False
    score: float = 0.0


class RecoveryPlan(BaseModel):
    plan_id: str
    task_id: str
    disruption_summary: str
    evaluated_options: list[RecoveryOption] = Field(default_factory=list)
    selected_option: RecoveryOption | None = None
    selected_option_rationale: str
    sla_risk: str
    status: str
    approvals: list[str] = Field(default_factory=list)
    execution_evidence: list[str] = Field(default_factory=list)
    audit_reference: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
