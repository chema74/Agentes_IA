from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UpstashRedisAdapter:
    url: str
    token: str
    mock_mode: bool = True
    values: dict[str, str] = field(default_factory=dict)

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def get(self, key: str) -> str | None:
        return self.values.get(key)
