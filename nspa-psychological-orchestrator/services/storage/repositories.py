from __future__ import annotations

from dataclasses import dataclass, field

from domain.affect.models import NeuroState
from domain.narrative.models import NarrativeEpisode
from domain.risk.models import RiskEvent


@dataclass
class OrchestratorStore:
    neuro_states: dict[str, NeuroState] = field(default_factory=dict)
    risk_events: dict[str, list[RiskEvent]] = field(default_factory=dict)
    episodes: dict[str, list[NarrativeEpisode]] = field(default_factory=dict)

    def save_neuro_state(self, state: NeuroState) -> None:
        self.neuro_states[state.user_id] = state

    def get_neuro_state(self, user_id: str) -> NeuroState | None:
        return self.neuro_states.get(user_id)

    def append_risk_event(self, event: RiskEvent) -> None:
        self.risk_events.setdefault(event.user_id, []).append(event)

    def append_episode(self, episode: NarrativeEpisode) -> None:
        self.episodes.setdefault(episode.user_id, []).append(episode)

    def get_recent_episodes(self, user_id: str, limit: int = 5) -> list[NarrativeEpisode]:
        return self.episodes.get(user_id, [])[-limit:]


STORE = OrchestratorStore()
