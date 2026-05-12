from __future__ import annotations

from domain.auctions.models import Bid
from domain.tasks.models import LogisticsTask


class GroqClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def score_recovery_option(self, task: LogisticsTask, bid: Bid) -> dict:
        sla_component = max(0.0, 1 - (bid.projected_total_delay_minutes / max(task.sla_target_minutes * 2, 1)))
        cost_ratio = max(0.0, (bid.offered_cost - task.base_cost) / max(task.base_cost, 1))
        cost_component = max(0.0, 1 - cost_ratio)
        score = (
            (sla_component * 0.35)
            + (cost_component * 0.20)
            + (bid.confidence_score * 0.20)
            + (0.15 if bid.regulatory_compliant else 0.0)
            + (0.10 if bid.operationally_feasible else 0.0)
        )
        tradeoffs = [
            f"incremental_cost_ratio={cost_ratio:.2f}",
            f"projected_total_delay_minutes={bid.projected_total_delay_minutes}",
            f"activation_minutes={bid.estimated_activation_minutes}",
            f"reliability={bid.confidence_score:.2f}",
        ]
        requires_human_approval = cost_ratio > 0.2 or bid.projected_total_delay_minutes > task.max_sla_breach_tolerance_minutes
        return {
            "score": round(score, 4),
            "confidence_score": round(min(1.0, (bid.confidence_score + sla_component) / 2), 4),
            "tradeoffs": tradeoffs,
            "requires_human_approval": requires_human_approval,
        }

    def explain_selection(self, selected_agent_id: str | None, options_count: int, status: str) -> str:
        if selected_agent_id is None:
            return f"No se selecciona peer automatico. status={status}. options_evaluated={options_count}."
        return f"Se selecciona {selected_agent_id} por equilibrio verificable entre SLA, coste incremental, fiabilidad y activacion. status={status}."


GROQ_CLIENT = GroqClient(model="llama3-8b-8192")
