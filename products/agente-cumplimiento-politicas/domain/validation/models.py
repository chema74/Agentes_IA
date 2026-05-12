from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class PredicateEvaluation(BaseModel):
    predicate_id: str
    predicate_name: str
    passed: bool
    actual_value: str | float | bool | None = None
    expected_value: str | float | bool | None = None
    failure_reason: str | None = None


class ValidationTrace(BaseModel):
    trace_id: str
    intent_id: str
    evaluated_predicates: list[PredicateEvaluation] = Field(default_factory=list)
    policy_ids: list[str] = Field(default_factory=list)
    state_assertions_used: list[str] = Field(default_factory=list)
    decision_path: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
