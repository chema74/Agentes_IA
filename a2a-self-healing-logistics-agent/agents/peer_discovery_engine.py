from __future__ import annotations

from domain.agent_cards.models import AgentCard
from domain.tasks.models import LogisticsTask


def summarize_discovery(task: LogisticsTask, cards: list[AgentCard]) -> dict:
    viable = [
        card for card in cards
        if task.mode in card.supported_modes and card.available_capacity >= task.capacity_required and card.is_fresh()
    ]
    return {
        "candidate_count": len(cards),
        "viable_peer_count": len(viable),
        "peer_ids": [card.agent_id for card in viable],
        "used_agent_cards": [card.agent_id for card in cards],
    }
