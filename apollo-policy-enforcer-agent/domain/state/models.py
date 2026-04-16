from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class StateAssertion(BaseModel):
    key: str
    value: str | float | bool
    source_of_truth: str
    freshness_minutes: int


class SymbolicState(BaseModel):
    entity_id: str
    entity_type: str
    assertions: list[StateAssertion] = Field(default_factory=list)
    inconsistencies_detected: list[str] = Field(default_factory=list)
    last_validated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
