from __future__ import annotations

from domain.plans.models import RecoveryOption
from domain.tasks.models import LogisticsTask


def assess_sla_risk(task: LogisticsTask, options: list[RecoveryOption]) -> str:
    if not options:
        return "critical"
    best = min(options, key=lambda item: item.projected_sla_breach_minutes)
    if best.projected_sla_breach_minutes <= 0:
        return "low"
    if best.projected_sla_breach_minutes <= task.max_sla_breach_tolerance_minutes:
        return "medium"
    return "high"
