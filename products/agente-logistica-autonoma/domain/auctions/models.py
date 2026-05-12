from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from domain.negotiation.models import NegotiationEvent


class Bid(BaseModel):
    agent_id: str
    offered_capacity: float
    offered_cost: float
    currency: str
    estimated_activation_minutes: int
    projected_total_delay_minutes: int
    confidence_score: float
    regulatory_compliant: bool = True
    operationally_feasible: bool = True


class BidAuction(BaseModel):
    auction_id: str
    task_id: str
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    bid_deadline: datetime
    currency: str
    constraints_snapshot: dict
    bids: list[Bid] = Field(default_factory=list)
    negotiation_log: list[NegotiationEvent] = Field(default_factory=list)
    winner_selection_rationale: str | None = None
    status: str = "open"
