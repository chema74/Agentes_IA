from __future__ import annotations

from datetime import datetime, UTC
from typing import Any


def make_audit_event(entity_type: str, entity_id: str, event_type: str, actor_user_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "event_type": event_type,
        "actor_user_id": actor_user_id,
        "payload_json": payload,
        "created_at": datetime.now(UTC).isoformat(),
    }
