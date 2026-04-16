from __future__ import annotations

from datetime import UTC, datetime

from core.safety.logistics_breaker import evaluate_logistics_breaker
from domain.plans.models import RecoveryOption
from domain.tasks.models import DisruptionEvent, LogisticsTask


def test_breaker_blocks_cost_violation():
    task = LogisticsTask(
        id="task-1",
        shipment_reference="SHIP-1",
        order_reference="ORD-1",
        origin="Algeciras",
        destination="Madrid",
        committed_pickup_at=datetime.now(UTC),
        committed_delivery_at=datetime.now(UTC),
        mode="road",
        capacity_required=12,
        capacity_unit="pallet",
        base_cost=1200,
        priority="critical",
        sla_target_minutes=300,
        authorized_incremental_cost=100,
        current_status="disrupted",
    )
    disruption = DisruptionEvent(id="dis-1", task_id="task-1", disruption_type="port_blockage", severity="critical", summary="Port blockage", estimated_delay_minutes=480)
    option = RecoveryOption(
        option_id="opt-1",
        agent_id="peer-1",
        execution_mode="reassignment",
        incremental_cost=250,
        projected_total_delay_minutes=180,
        projected_sla_breach_minutes=0,
        activation_minutes=40,
        reliability_score=0.9,
        confidence_score=0.9,
    )
    result = evaluate_logistics_breaker(task, disruption, option)
    assert result.status == "BLOCKED"
    assert "COST_THRESHOLD_EXCEEDED" in result.reason_codes


def test_breaker_blocks_missing_data():
    task = LogisticsTask(
        id="task-2",
        shipment_reference="SHIP-2",
        order_reference="ORD-2",
        origin="Lisbon",
        destination="Madrid",
        committed_pickup_at=datetime.now(UTC),
        committed_delivery_at=datetime.now(UTC),
        mode="road",
        capacity_required=6,
        capacity_unit="pallet",
        base_cost=800,
        priority="high",
        sla_target_minutes=240,
        authorized_incremental_cost=250,
        current_status="delayed",
    )
    disruption = DisruptionEvent(id="dis-2", task_id="task-2", disruption_type="weather", severity="high", summary="Storm impact", estimated_delay_minutes=150)
    option = RecoveryOption(
        option_id="opt-2",
        agent_id="peer-1",
        execution_mode="reassignment",
        incremental_cost=90,
        projected_total_delay_minutes=130,
        projected_sla_breach_minutes=0,
        activation_minutes=30,
        reliability_score=0.8,
        confidence_score=0.6,
        missing_critical_data=True,
    )
    result = evaluate_logistics_breaker(task, disruption, option)
    assert result.status == "BLOCKED"
    assert "INSUFFICIENT_DATA" in result.reason_codes
