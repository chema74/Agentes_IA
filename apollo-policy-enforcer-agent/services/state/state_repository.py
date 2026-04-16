from __future__ import annotations

from domain.state.models import StateAssertion, SymbolicState


class StateRepository:
    def build_symbolic_state(self, entity_id: str, entity_type: str, context: dict) -> SymbolicState:
        assertions = []
        inconsistencies = []
        for key, value in context.items():
            assertions.append(
                StateAssertion(
                    key=key,
                    value=value,
                    source_of_truth="request_context",
                    freshness_minutes=1,
                )
            )
        if context.get("state_conflict") is True:
            inconsistencies.append("Explicit conflict flag provided in context.")
        return SymbolicState(entity_id=entity_id, entity_type=entity_type, assertions=assertions, inconsistencies_detected=inconsistencies)


STATE_REPOSITORY = StateRepository()
