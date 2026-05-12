from __future__ import annotations

from domain.tasks.models import DisruptionEvent, LogisticsTask


def assess_disruption(task: LogisticsTask, disruption: DisruptionEvent) -> dict:
    delay_ratio = disruption.estimated_delay_minutes / max(task.sla_target_minutes, 1)
    threatens_sla = disruption.estimated_delay_minutes > task.max_sla_breach_tolerance_minutes
    status = "at_risk" if delay_ratio >= 0.25 else "stable"
    if threatens_sla or disruption.severity in {"high", "critical"}:
        status = "disrupted"
    return {
        "disruption_status": status,
        "delay_ratio": round(delay_ratio, 2),
        "threatens_sla": threatens_sla,
        "summary": disruption.summary,
    }
