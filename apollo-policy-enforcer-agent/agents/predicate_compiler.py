from __future__ import annotations

from domain.intents.models import TypedIntent
from domain.policies.models import PolicyConflict
from services.policies.policy_repository import POLICY_REPOSITORY


def compile_predicates(typed_intent: TypedIntent):
    rules = POLICY_REPOSITORY.fetch_matching_rules(typed_intent.action_type)
    conflicts: list[PolicyConflict] = []
    if len({rule.decision_on_failure for rule in rules}) > 1 and len(rules) > 1:
        conflicts.append(
            PolicyConflict(
                conflict_code="DIVERGENT_FAILURE_ACTION",
                message="Matched policies disagree on failure handling.",
                policy_ids=[rule.policy_id for rule in rules],
            )
        )
    predicates = [predicate for rule in rules for predicate in rule.predicates]
    return rules, predicates, conflicts
