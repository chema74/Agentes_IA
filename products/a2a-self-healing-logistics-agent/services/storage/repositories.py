from __future__ import annotations

from dataclasses import dataclass, field

from domain.audit.models import AuditEvent
from domain.auctions.models import BidAuction
from domain.plans.models import RecoveryPlan
from domain.tasks.models import LogisticsTask


@dataclass
class InMemoryStore:
    mode: str = "fallback-local"
    tasks: dict[str, LogisticsTask] = field(default_factory=dict)
    auctions: dict[str, BidAuction] = field(default_factory=dict)
    recovery_plans: dict[str, RecoveryPlan] = field(default_factory=dict)
    audit_events: dict[str, list[AuditEvent]] = field(default_factory=dict)

    def append_audit_event(self, event: AuditEvent) -> None:
        self.audit_events.setdefault(event.reference, []).append(event)

    def audit_events_by_reference(self, reference: str) -> list[AuditEvent]:
        return self.audit_events.get(reference, [])


STORE = InMemoryStore()
