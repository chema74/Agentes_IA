from __future__ import annotations

from pydantic import BaseModel, Field

from domain.intents.models import TypedIntent
from domain.policies.models import PolicyConflict, PolicyRule
from domain.state.models import SymbolicState
from domain.validation.models import ValidationTrace


class PolicyBreakerDecision(BaseModel):
    status: str
    reason_codes: list[str] = Field(default_factory=list)
    human_review_required: bool
    notes: list[str] = Field(default_factory=list)


def evaluate_policy_breaker(
    typed_intent: TypedIntent,
    matched_rules: list[PolicyRule],
    symbolic_state: SymbolicState,
    validation_trace: ValidationTrace,
    conflicts: list[PolicyConflict],
) -> PolicyBreakerDecision:
    reasons: list[str] = []
    if typed_intent.confidence_score < 0.6:
        reasons.append("UNTYPABLE_OR_LOW_CONFIDENCE_INTENT")
    if not matched_rules:
        reasons.append("NO_APPLICABLE_POLICY")
    if conflicts:
        reasons.append("POLICY_CONFLICT_DETECTED")
    if symbolic_state.inconsistencies_detected:
        reasons.append("SYMBOLIC_STATE_CONTRADICTION")
    if any(not evaluation.passed for evaluation in validation_trace.evaluated_predicates if evaluation.failure_reason == "missing_predicate_input"):
        reasons.append("INSUFFICIENT_PREDICATE_EVIDENCE")
    if reasons:
        return PolicyBreakerDecision(
            status="BLOCKED",
            reason_codes=reasons,
            human_review_required=True,
            notes=["El Policy Circuit Breaker detiene la accion por insuficiencia o conflicto logico."],
        )
    if any(not evaluation.passed for evaluation in validation_trace.evaluated_predicates):
        return PolicyBreakerDecision(
            status="REQUIRES_REVIEW",
            reason_codes=["POLICY_VALIDATION_FAILED"],
            human_review_required=True,
            notes=["La accion no supera validacion formal suficiente para autorizacion automatica."],
        )
    return PolicyBreakerDecision(status="AUTHORIZED", human_review_required=False, notes=["La accion supera validacion simbolica y de politica."])
