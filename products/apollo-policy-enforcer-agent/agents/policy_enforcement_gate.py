from __future__ import annotations

from domain.policies.models import PolicyConflict, PolicyRule
from domain.validation.models import ValidationTrace


def decide_policy_outcome(rules: list[PolicyRule], validation_trace: ValidationTrace, conflicts: list[PolicyConflict]) -> tuple[str, list[str]]:
    if conflicts:
        return "BLOCKED", [conflict.message for conflict in conflicts]
    failures = [evaluation for evaluation in validation_trace.evaluated_predicates if not evaluation.passed]
    if not rules:
        return "BLOCKED", ["No matching formal policy."]
    if not failures:
        return "AUTHORIZED", []
    highest = rules[0]
    if any(item.failure_reason == "missing_predicate_input" for item in failures):
        return "BLOCKED", ["Missing predicate input."]
    return highest.decision_on_failure, [item.predicate_name for item in failures]
