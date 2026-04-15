from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SupabaseClientAdapter:
    url: str
    key: str
    mock_mode: bool = True
    tables: dict[str, list[dict]] = field(default_factory=dict)

    def insert(self, table: str, payload: dict) -> dict:
        self.tables.setdefault(table, []).append(payload)
        return payload
