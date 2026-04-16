from __future__ import annotations

from datetime import UTC, datetime

from domain.tasks.models import DisruptionEvent, LogisticsTask
from services.discovery.a2a_registry import A2A_REGISTRY
from services.negotiation.a2a_negotiator import A2A_NEGOTIATOR


def test_negotiation_auction_logs_all_bids():
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
        authorized_incremental_cost=400,
        current_status="delayed",
    )
    disruption = DisruptionEvent(id="dis-1", task_id="task-1", disruption_type="port_delay", severity="high", summary="Road feeder delay", estimated_delay_minutes=220)
    cards = A2A_REGISTRY.fetch_agent_cards()
    auction = A2A_NEGOTIATOR.open_auction(task, disruption, cards)
    assert auction.status == "completed"
    assert len(auction.bids) >= 1
    assert len(auction.negotiation_log) >= len(auction.bids) * 2
