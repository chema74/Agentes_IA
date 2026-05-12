from __future__ import annotations

from datetime import UTC, datetime, timedelta

from domain.agent_cards.models import AgentCard


class A2ARegistry:
    def fetch_agent_cards(self) -> list[AgentCard]:
        now = datetime.now(UTC)
        return [
            AgentCard(
                agent_id="peer-eu-road-01",
                legal_entity="Euro Relay Logistics",
                capabilities=["capacity_swap", "reroute", "hot_shot"],
                supported_modes=["road"],
                supported_regions=["EU"],
                lanes=["MAD-BCN", "MAD-BILBAO"],
                available_capacity=18.0,
                capacity_unit="pallet",
                pricing_model="spot",
                historical_reliability=0.91,
                compliance_declarations=["ADR", "GDP"],
                a2a_endpoint="https://peer-eu-road-01.example/a2a",
                mcp_methods=["reserve_capacity", "confirm_reassignment"],
                freshness_timestamp=now,
            ),
            AgentCard(
                agent_id="peer-eu-multimodal-02",
                legal_entity="Continental Capacity Mesh",
                capabilities=["capacity_swap", "cross_dock"],
                supported_modes=["road", "rail", "sea"],
                supported_regions=["EU", "MED"],
                lanes=["VAL-GEN", "ALG-MRS"],
                available_capacity=30.0,
                capacity_unit="pallet",
                pricing_model="dynamic",
                historical_reliability=0.87,
                compliance_declarations=["Customs-bonded"],
                a2a_endpoint="https://peer-eu-multimodal-02.example/a2a",
                mcp_methods=["reserve_capacity", "issue_amendment"],
                freshness_timestamp=now - timedelta(hours=1),
            ),
        ]


A2A_REGISTRY = A2ARegistry()
