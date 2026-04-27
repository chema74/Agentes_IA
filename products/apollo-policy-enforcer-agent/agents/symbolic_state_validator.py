from __future__ import annotations

from uuid import uuid4

from domain.intents.models import TypedIntent
from domain.policies.models import PolicyPredicate
from domain.state.models import SymbolicState
from domain.validation.models import PredicateEvaluation, ValidationTrace


def validate_symbolic_state(typed_intent: TypedIntent, predicates: list[PolicyPredicate], symbolic_state: SymbolicState) -> ValidationTrace:
    evaluations: list[PredicateEvaluation] = []
    state_map = {assertion.key: assertion.value for assertion in symbolic_state.assertions}
    for predicate in predicates:
        actual = _resolve_actual_value(predicate.name, typed_intent, state_map)
        if actual is None:
            evaluations.append(
                PredicateEvaluation(
                    predicate_id=predicate.predicate_id,
                    predicate_name=predicate.name,
                    passed=False,
                    expected_value=predicate.expected_value,
                    failure_reason="missing_predicate_input",
                )
            )
            continue
        passed = _compare(predicate.operator, actual, predicate.expected_value)
        evaluations.append(
            PredicateEvaluation(
                predicate_id=predicate.predicate_id,
                predicate_name=predicate.name,
                passed=passed,
                actual_value=actual,
                expected_value=predicate.expected_value,
                failure_reason=None if passed else "predicate_mismatch",
            )
        )
    return ValidationTrace(
        trace_id=f"trace-{uuid4().hex[:10]}",
        intent_id=typed_intent.intent_id,
        evaluated_predicates=evaluations,
        state_assertions_used=list(state_map.keys()),
        decision_path=["intent_typed", "predicates_compiled", "state_validated"],
    )


def _resolve_actual_value(predicate_name: str, typed_intent: TypedIntent, state_map: dict):
    mapping = {
        "spend_under_limit": typed_intent.amount,
        "finance_approval_present": state_map.get("finance_approval_present"),
        "jurisdiction_approved": typed_intent.jurisdiction,
        "dpo_approval_present": state_map.get("dpo_approval_present"),
        "contract_status_active": state_map.get("contract_status"),
        "legal_approval_present": state_map.get("legal_approval_present"),
    }
    return mapping.get(predicate_name)


def _compare(operator: str, actual, expected) -> bool:
    if operator == "==":
        return actual == expected
    if operator == "<=":
        return float(actual) <= float(expected)
    if operator == "in":
        return actual == expected
    return False
