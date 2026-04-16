from __future__ import annotations

from domain.intents.models import TypedIntent
from agents.predicate_compiler import compile_predicates


def test_predicate_compiler_returns_matching_rules():
    typed_intent = TypedIntent(
        intent_id="intent-1",
        action_type="transfer_data",
        target_resource="dataset-1",
        actor_id="user-1",
        jurisdiction="EU",
        confidence_score=0.9,
        source_text="transfer data",
    )
    rules, predicates, conflicts = compile_predicates(typed_intent)
    assert len(rules) == 1
    assert len(predicates) == 2
    assert conflicts == []
