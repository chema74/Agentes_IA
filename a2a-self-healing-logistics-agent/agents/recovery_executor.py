from __future__ import annotations

from domain.plans.models import RecoveryPlan
from services.governance.mcp_executor import MCP_EXECUTOR


def execute_selected_plan(plan: RecoveryPlan) -> list[str]:
    if plan.selected_option is None:
        return []
    return MCP_EXECUTOR.execute_recovery_plan(plan)
