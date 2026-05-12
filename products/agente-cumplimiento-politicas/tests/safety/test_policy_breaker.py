from __future__ import annotations

from uuid import uuid4

from core.safety.policy_breaker import evaluate_policy_breaker
from domain.intents.models import TypedIntent
from domain.policies.models import PolicyConflict, PolicyPredicate, PolicyRule
from domain.state.models import SymbolicState
from domain.validation.models import PredicateEvaluation, ValidationTrace


def test_breaker_blocks_low_confidence_and_missing_policy():
    typed_intent = TypedIntent(
        intent_id="intent-1",
        action_type="unknown",
        target_resource="resource-1",
        actor_id="user-1",
        confidence_score=0.4,
        source_text="do something",
    )
    state = SymbolicState(entity_id="resource-1", entity_type="resource")
    trace = ValidationTrace(trace_id=f"trace-{uuid4().hex[:8]}", intent_id="intent-1")
    result = evaluate_policy_breaker(typed_intent, [], state, trace, [])
    assert result.status == "BLOCKED"
    assert "UNTYPABLE_OR_LOW_CONFIDENCE_INTENT" in result.reason_codes
    assert "NO_APPLICABLE_POLICY" in result.reason_codes


def test_breaker_blocks_state_contradiction():
    typed_intent = TypedIntent(
        intent_id="intent-2",
        action_type="approve_spend",
        target_resource="invoice-1",
        actor_id="user-1",
        confidence_score=0.9,
        source_text="approve spend",
    )
    rule = PolicyRule(
        policy_id="p1",
        name="rule",
        action_types=["approve_spend"],
        predicates=[PolicyPredicate(predicate_id="pred-1", name="finance_approval_present", description="d", predicate_type="approval", operator="==", expected_value=True, severity="critical", source_policy_id="p1", priority=10)],
        decision_on_failure="BLOCKED",
        priority=10,
        description="desc",
    )
    state = SymbolicState(entity_id="invoice-1", entity_type="invoice", inconsistencies_detected=["Contradictory approval sources"])
    trace = ValidationTrace(
        trace_id=f"trace-{uuid4().hex[:8]}",
        intent_id="intent-2",
        evaluated_predicates=[PredicateEvaluation(predicate_id="pred-1", predicate_name="finance_approval_present", passed=True, actual_value=True, expected_value=True)],
    )
    result = evaluate_policy_breaker(typed_intent, [rule], state, trace, [])
    assert result.status == "BLOCKED"
    assert "SYMBOLIC_STATE_CONTRADICTION" in result.reason_codes
