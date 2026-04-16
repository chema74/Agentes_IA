from __future__ import annotations

from typing import Protocol

from domain.audit.models import AuditEvent
from domain.cases.models import ChangeCase


class CaseStore(Protocol):
    mode: str

    def save_case(self, item: ChangeCase) -> None: ...

    def get_case(self, case_id: str) -> ChangeCase | None: ...

    def append_audit_event(self, event: AuditEvent) -> None: ...

    def audit_events_by_reference(self, reference: str) -> list[AuditEvent]: ...

    def health(self) -> dict: ...


class CacheStore(Protocol):
    mode: str

    def set_json(self, key: str, value: dict) -> None: ...

    def get_json(self, key: str) -> dict | None: ...

    def health(self) -> dict: ...


class VectorStore(Protocol):
    mode: str

    def index_case(self, item: ChangeCase) -> None: ...

    def health(self) -> dict: ...
