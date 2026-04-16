from __future__ import annotations

from agents.natural_language_intent_encoder import encode_typed_intent


def test_intent_encoder_types_spend_action():
    typed = encode_typed_intent(
        text="Please approve spend for the vendor invoice",
        actor_id="user-1",
        target_resource="invoice-1",
        context={"amount": 2000, "currency": "EUR"},
    )
    assert typed.action_type == "approve_spend"
    assert typed.confidence_score >= 0.9
