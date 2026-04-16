from __future__ import annotations

from datetime import UTC, datetime, timedelta

from domain.agent_cards.models import AgentCard


def test_agent_card_freshness_validation():
    fresh = AgentCard(
        agent_id="peer-1",
        legal_entity="Peer 1",
        capabilities=["capacity_swap"],
        supported_modes=["road"],
        supported_regions=["EU"],
        available_capacity=10,
        capacity_unit="pallet",
        pricing_model="spot",
        historical_reliability=0.9,
        a2a_endpoint="https://example.com",
        freshness_timestamp=datetime.now(UTC),
    )
    stale = fresh.model_copy(update={"agent_id": "peer-2", "freshness_timestamp": datetime.now(UTC) - timedelta(hours=30)})
    assert fresh.is_fresh() is True
    assert stale.is_fresh() is False
