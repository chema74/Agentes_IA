from __future__ import annotations

from services.llm.sambanova_client import SAMBANOVA_CLIENT


def encode_typed_intent(text: str, actor_id: str, target_resource: str, context: dict):
    return SAMBANOVA_CLIENT.encode_intent(text=text, actor_id=actor_id, target_resource=target_resource, context=context)
