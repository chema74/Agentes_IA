from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    agent_id: str
    legal_entity: str
    capabilities: list[str]
    supported_modes: list[str]
    supported_regions: list[str]
    lanes: list[str] = Field(default_factory=list)
    available_capacity: float
    capacity_unit: str
    pricing_model: str
    historical_reliability: float
    compliance_declarations: list[str] = Field(default_factory=list)
    a2a_endpoint: str
    mcp_methods: list[str] = Field(default_factory=list)
    freshness_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def is_fresh(self, max_age_hours: int = 24) -> bool:
        return self.freshness_timestamp >= datetime.now(UTC) - timedelta(hours=max_age_hours)
