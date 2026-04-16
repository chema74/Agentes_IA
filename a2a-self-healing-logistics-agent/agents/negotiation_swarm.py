from __future__ import annotations

from domain.auctions.models import Bid
from domain.plans.models import RecoveryOption
from domain.tasks.models import LogisticsTask
from services.llm.groq_client import GROQ_CLIENT


def build_recovery_options(task: LogisticsTask, bids: list[Bid]) -> list[RecoveryOption]:
    options: list[RecoveryOption] = []
    for index, bid in enumerate(bids, start=1):
        score = GROQ_CLIENT.score_recovery_option(task=task, bid=bid)
        projected_breach = max(0, bid.projected_total_delay_minutes - task.sla_target_minutes)
        options.append(
            RecoveryOption(
                option_id=f"option-{index}",
                agent_id=bid.agent_id,
                execution_mode="reassignment",
                incremental_cost=max(0.0, bid.offered_cost - task.base_cost),
                projected_total_delay_minutes=bid.projected_total_delay_minutes,
                projected_sla_breach_minutes=projected_breach,
                activation_minutes=bid.estimated_activation_minutes,
                reliability_score=bid.confidence_score,
                regulatory_compliant=bid.regulatory_compliant,
                operationally_feasible=bid.operationally_feasible,
                confidence_score=score["confidence_score"],
                tradeoffs=score["tradeoffs"],
                requires_human_approval=score["requires_human_approval"],
                score=score["score"],
            )
        )
    return options
