from __future__ import annotations

from datetime import UTC, datetime

from agents.sla_guardian import assess_sla_risk
from domain.plans.models import RecoveryOption
from domain.tasks.models import LogisticsTask


def test_sla_risk_high_when_best_option_still_breaches_tolerance():
    task = LogisticsTask(
        id="task-1",
        shipment_reference="SHIP-1",
        order_reference="ORD-1",
        origin="Madrid",
        destination="Valencia",
        committed_pickup_at=datetime.now(UTC),
        committed_delivery_at=datetime.now(UTC),
        mode="road",
        capacity_required=8,
        capacity_unit="pallet",
        base_cost=900,
        priority="critical",
        sla_target_minutes=180,
        max_sla_breach_tolerance_minutes=30,
        authorized_incremental_cost=200,
        current_status="blocked",
    )
    option = RecoveryOption(
        option_id="opt-1",
        agent_id="peer-1",
        execution_mode="reassignment",
        incremental_cost=100,
        projected_total_delay_minutes=260,
        projected_sla_breach_minutes=80,
        activation_minutes=50,
        reliability_score=0.8,
        confidence_score=0.8,
    )
    assert assess_sla_risk(task, [option]) == "high"
