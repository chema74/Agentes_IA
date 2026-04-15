from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NeonVectorStoreAdapter:
    database_url: str
    collection_name: str
    enabled: bool = False
    memory_rows: list[dict] = field(default_factory=list)

    def add_episode(self, payload: dict) -> None:
        self.memory_rows.append(payload)

    def search(self, text: str, limit: int = 5) -> list[dict]:
        lowered = text.lower()
        ranked = []
        for row in self.memory_rows:
            score = sum(1 for token in lowered.split() if len(token) > 3 and token in row.get("summary", "").lower())
            ranked.append((score, row))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in ranked[:limit] if item[0] > 0]
