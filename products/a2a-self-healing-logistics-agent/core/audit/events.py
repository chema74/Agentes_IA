from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from domain.audit.models import AuditEvent


def make_audit_event(reference: str, entity_type: str, entity_id: str, action: str, payload: dict) -> AuditEvent:
    return AuditEvent(
        id=f"audit-{uuid4().hex[:12]}",
        reference=reference,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        payload=payload,
        created_at=datetime.now(UTC),
    )
