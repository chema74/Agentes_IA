from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class LogisticsTask(BaseModel):
    id: str
    shipment_reference: str
    order_reference: str
    origin: str
    destination: str
    committed_pickup_at: datetime
    committed_delivery_at: datetime
    mode: str
    capacity_required: float
    capacity_unit: str
    base_cost: float
    currency: str = "EUR"
    priority: str
    sla_target_minutes: int
    max_sla_breach_tolerance_minutes: int = 120
    authorized_incremental_cost: float
    operational_constraints: list[str] = Field(default_factory=list)
    regulatory_constraints: list[str] = Field(default_factory=list)
    service_tier: str = "standard"
    current_status: str


class DisruptionEvent(BaseModel):
    id: str
    task_id: str
    disruption_type: str
    severity: str
    summary: str
    reported_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    location: str | None = None
    estimated_delay_minutes: int = 0
    affected_capacity_delta: float = 0.0
    evidence_refs: list[str] = Field(default_factory=list)
