from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from agents.deterministic_decoder import build_explanation
from agents.natural_language_intent_encoder import encode_typed_intent
from agents.policy_enforcement_gate import decide_policy_outcome
from agents.predicate_compiler import compile_predicates
from agents.symbolic_state_validator import validate_symbolic_state
from core.audit.events import make_audit_event
from core.safety.policy_breaker import evaluate_policy_breaker
from domain.mandates.models import ActionMandate
from services.policies.policy_repository import POLICY_REPOSITORY
from services.state.state_repository import STATE_REPOSITORY
from services.storage.repositories import STORE


class OrchestratorInput(BaseModel):
    request_text: str
    actor_id: str
    target_resource: str
    context: dict = Field(default_factory=dict)
    request_id: str | None = None
    idempotency_key: str | None = None


class OrchestratorOutput(BaseModel):
    typed_intent: dict
    matched_predicates: list[dict]
    symbolic_state: dict
    validation_trace: dict
    conflicts_detected: list[dict]
    action_mandate: dict
    explanation: str
    audit_reference: str


class PolicyOrchestrator:
    def validate(self, payload: OrchestratorInput) -> OrchestratorOutput:
        return self._run(payload, persist_mandate=False)

    def enforce(self, payload: OrchestratorInput) -> OrchestratorOutput:
        if payload.idempotency_key:
            existing_response = STORE.get_idempotent_response(payload.idempotency_key)
            if existing_response is not None:
                return OrchestratorOutput.model_validate(existing_response)
        return self._run(payload, persist_mandate=True)

    def _run(self, payload: OrchestratorInput, persist_mandate: bool) -> OrchestratorOutput:
        typed_intent = encode_typed_intent(
            text=payload.request_text,
            actor_id=payload.actor_id,
            target_resource=payload.target_resource,
            context=payload.context,
        )
        rules, predicates, conflicts = compile_predicates(typed_intent)
        symbolic_state = STATE_REPOSITORY.build_symbolic_state(
            entity_id=payload.target_resource,
            entity_type=payload.context.get("entity_type", "resource"),
            context=payload.context,
        )
        validation_trace = validate_symbolic_state(typed_intent, predicates, symbolic_state)
        validation_trace.policy_ids = [rule.policy_id for rule in rules]
        decision_hint, failure_reasons = decide_policy_outcome(rules, validation_trace, conflicts)
        breaker = evaluate_policy_breaker(typed_intent, rules, symbolic_state, validation_trace, conflicts)
        final_decision = breaker.status if breaker.status != "AUTHORIZED" else decision_hint
        audit_reference = f"audit-ref-{uuid4().hex[:10]}"
        explanation = build_explanation(final_decision, failure_reasons or breaker.reason_codes)
        mandate = ActionMandate(
            mandate_id=f"mandate-{uuid4().hex[:10]}",
            typed_intent=typed_intent,
            decision=final_decision,
            constraints_applied=[predicate.name for predicate in predicates],
            actor_id=payload.actor_id,
            target_resource=payload.target_resource,
            explanation=explanation,
            audit_reference=audit_reference,
        )
        output = OrchestratorOutput(
            typed_intent=typed_intent.model_dump(mode="json"),
            matched_predicates=[predicate.model_dump(mode="json") for predicate in predicates],
            symbolic_state=symbolic_state.model_dump(mode="json"),
            validation_trace=validation_trace.model_dump(mode="json"),
            conflicts_detected=[conflict.model_dump(mode="json") for conflict in conflicts],
            action_mandate=mandate.model_dump(mode="json"),
            explanation=explanation,
            audit_reference=audit_reference,
        )
        if persist_mandate:
            STORE.save_mandate(mandate, idempotency_key=payload.idempotency_key)
            STORE.save_idempotent_response(payload.idempotency_key, output.model_dump(mode="json"))
        STORE.save_trace(validation_trace)
        self._append_event(
            audit_reference,
            "TYPED_INTENT",
            typed_intent.intent_id,
            "typed",
            {"action_type": typed_intent.action_type, "request_id": payload.request_id, "idempotency_key": payload.idempotency_key},
        )
        self._append_event(audit_reference, "VALIDATION_TRACE", validation_trace.trace_id, "validated", {"decision": final_decision, "request_id": payload.request_id})
        self._append_event(
            audit_reference,
            "ACTION_MANDATE",
            mandate.mandate_id,
            "created",
            {"decision": final_decision, "persisted": persist_mandate, "request_id": payload.request_id},
        )
        return output

    def _append_event(self, reference: str, entity_type: str, entity_id: str, action: str, payload: dict) -> None:
        STORE.append_audit_event(make_audit_event(reference, entity_type, entity_id, action, payload))


ORCHESTRATOR = PolicyOrchestrator()
