from __future__ import annotations

from domain.plans.models import RecoveryPlan


class MCPExecutor:
    def execute_recovery_plan(self, plan: RecoveryPlan) -> list[str]:
        if plan.selected_option is None:
            return []
        option = plan.selected_option
        return [f"mcp.reserve_capacity:{option.agent_id}", f"mcp.confirm_reassignment:{plan.task_id}"]


MCP_EXECUTOR = MCPExecutor()
