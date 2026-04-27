from __future__ import annotations

from uuid import uuid4

from agents.policy_enforcement_gate import decide_policy_outcome
from domain.policies.models import PolicyConflict, PolicyPredicate, PolicyRule
from domain.validation.models import PredicateEvaluation, ValidationTrace


def test_gate_blocks_on_conflict():
    rule = PolicyRule(
        policy_id="p1",
        name="rule",
        action_types=["approve_spend"],
        predicates=[],
        decision_on_failure="BLOCKED",
        priority=100,
        description="desc",
    )
    trace = ValidationTrace(trace_id=f"trace-{uuid4().hex[:8]}", intent_id="intent-1")
    decision, reasons = decide_policy_outcome([rule], trace, [PolicyConflict(conflict_code="C1", message="Conflict")])
    assert decision == "BLOCKED"
    assert reasons == ["Conflict"]


def test_gate_allows_when_all_predicates_pass():
    rule = PolicyRule(
        policy_id="p1",
        name="rule",
        action_types=["approve_spend"],
        predicates=[PolicyPredicate(predicate_id="pred-1", name="x", description="d", predicate_type="state", operator="==", expected_value=True, severity="high", source_policy_id="p1", priority=1)],
        decision_on_failure="BLOCKED",
        priority=100,
        description="desc",
    )
    trace = ValidationTrace(
        trace_id=f"trace-{uuid4().hex[:8]}",
        intent_id="intent-1",
        evaluated_predicates=[PredicateEvaluation(predicate_id="pred-1", predicate_name="x", passed=True, actual_value=True, expected_value=True)],
    )
    decision, reasons = decide_policy_outcome([rule], trace, [])
    assert decision == "AUTHORIZED"
    assert reasons == []
