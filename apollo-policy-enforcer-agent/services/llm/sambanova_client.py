from __future__ import annotations

from uuid import uuid4

from domain.intents.models import TypedIntent


class SambaNovaClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def encode_intent(self, text: str, actor_id: str, target_resource: str, context: dict) -> TypedIntent:
        lowered = text.lower()
        action_type = "request_review"
        amount = context.get("amount")
        currency = context.get("currency", "EUR")
        data_domain = context.get("data_domain")
        jurisdiction = context.get("jurisdiction")
        confidence = 0.58
        if "spend" in lowered or "gasto" in lowered or "approve invoice" in lowered:
            action_type = "approve_spend"
            confidence = 0.9
        elif "transfer" in lowered and "data" in lowered:
            action_type = "transfer_data"
            confidence = 0.92
        elif "contract" in lowered and ("amend" in lowered or "modify" in lowered):
            action_type = "amend_contract"
            confidence = 0.88
        return TypedIntent(
            intent_id=f"intent-{uuid4().hex[:10]}",
            action_type=action_type,
            target_resource=target_resource,
            actor_id=actor_id,
            amount=amount,
            currency=currency,
            data_domain=data_domain,
            jurisdiction=jurisdiction,
            confidence_score=confidence,
            source_text=text,
            extracted_attributes=context,
        )

    def explain_decision(self, decision: str, failure_reasons: list[str]) -> str:
        if decision == "AUTHORIZED":
            return "La accion queda autorizada porque la intencion tipada, los predicates y el estado simbolico son compatibles."
        return f"La accion no queda autorizada. Motivos formales: {', '.join(failure_reasons) if failure_reasons else 'validacion insuficiente'}."


SAMBANOVA_CLIENT = SambaNovaClient(model="Meta-Llama-3.1-8B-Instruct")
