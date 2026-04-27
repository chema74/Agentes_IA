from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class NegotiationEvent(BaseModel):
    id: str
    auction_id: str
    agent_id: str
    event_type: str
    message: str
    offered_capacity: float
    offered_cost: float
    currency: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
