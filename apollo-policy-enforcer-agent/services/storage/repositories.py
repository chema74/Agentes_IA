from __future__ import annotations

from dataclasses import dataclass, field

from domain.audit.models import AuditEvent
from domain.mandates.models import ActionMandate
from domain.policies.models import PolicyRule
from domain.validation.models import ValidationTrace


@dataclass
class InMemoryStore:
    mode: str = "fallback-local"
    policies: dict[str, PolicyRule] = field(default_factory=dict)
    mandates: dict[str, ActionMandate] = field(default_factory=dict)
    traces: dict[str, ValidationTrace] = field(default_factory=dict)
    audit_events: dict[str, list[AuditEvent]] = field(default_factory=dict)

    def append_audit_event(self, event: AuditEvent) -> None:
        self.audit_events.setdefault(event.reference, []).append(event)

    def audit_events_by_reference(self, reference: str) -> list[AuditEvent]:
        return self.audit_events.get(reference, [])


STORE = InMemoryStore()
