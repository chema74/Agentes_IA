from __future__ import annotations

from datetime import UTC, datetime

from domain.auctions.models import Bid
from domain.tasks.models import LogisticsTask
from services.llm.groq_client import GROQ_CLIENT


def test_scoring_prefers_lower_delay_and_cost():
    task = LogisticsTask(
        id="task-1",
        shipment_reference="SHIP-1",
        order_reference="ORD-1",
        origin="Madrid",
        destination="Barcelona",
        committed_pickup_at=datetime.now(UTC),
        committed_delivery_at=datetime.now(UTC),
        mode="road",
        capacity_required=10,
        capacity_unit="pallet",
        base_cost=1000,
        priority="high",
        sla_target_minutes=240,
        authorized_incremental_cost=350,
        current_status="in_transit",
    )
    better = Bid(agent_id="peer-a", offered_capacity=10, offered_cost=1080, currency="EUR", estimated_activation_minutes=45, projected_total_delay_minutes=90, confidence_score=0.9)
    worse = Bid(agent_id="peer-b", offered_capacity=10, offered_cost=1300, currency="EUR", estimated_activation_minutes=120, projected_total_delay_minutes=260, confidence_score=0.75)
    assert GROQ_CLIENT.score_recovery_option(task, better)["score"] > GROQ_CLIENT.score_recovery_option(task, worse)["score"]
