from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MCPConnectorAdapter:
    mock_mode: bool = True
    events: list[dict] = field(default_factory=list)

    def pull_activity(self, source: str, student_id: str) -> list[dict]:
        return [item for item in self.events if item.get("source") == source and item.get("student_id") == student_id]
