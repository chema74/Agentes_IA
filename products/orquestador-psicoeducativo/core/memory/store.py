from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NarrativeMemoryStore:
    episodes_by_user: dict[str, list[dict]] = field(default_factory=dict)

    def append_episode(self, user_id: str, episode: dict) -> None:
        self.episodes_by_user.setdefault(user_id, []).append(episode)

    def get_recent(self, user_id: str, limit: int = 5) -> list[dict]:
        return self.episodes_by_user.get(user_id, [])[-limit:]


MEMORY_STORE = NarrativeMemoryStore()
