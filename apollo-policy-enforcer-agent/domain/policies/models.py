from __future__ import annotations

from pydantic import BaseModel, Field


class PolicyPredicate(BaseModel):
    predicate_id: str
    name: str
    description: str
    predicate_type: str
    operator: str
    expected_value: str | float | bool
    severity: str
    source_policy_id: str
    priority: int
    required: bool = True


class PolicyRule(BaseModel):
    policy_id: str
    name: str
    action_types: list[str]
    predicates: list[PolicyPredicate]
    decision_on_failure: str
    priority: int
    description: str


class PolicyConflict(BaseModel):
    conflict_code: str
    message: str
    policy_ids: list[str] = Field(default_factory=list)
