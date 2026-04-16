from __future__ import annotations

import json
from dataclasses import dataclass
from threading import Lock

from core.config.settings import settings
from core.db.session import get_connection, init_db
from domain.audit.models import AuditEvent
from domain.cases.models import ChangeCase
from services.storage.base import CacheStore, CaseStore, VectorStore
from services.storage.neon_vector_store import NeonPgVectorStore, NoopVectorStore
from services.storage.supabase_adapter import SupabaseStore
from services.storage.upstash_adapter import InMemoryCache, UpstashRedisCache


@dataclass
class SqlStore:
    mode: str = "sql-backed"

    def __post_init__(self) -> None:
        self._lock = Lock()
        init_db()

    def save_case(self, item: ChangeCase) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO change_cases (
                    case_id, process_status, friction_level, human_review_required,
                    supervision_gate_status, audit_reference, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.case_id,
                    item.estado_del_proceso_de_cambio,
                    item.nivel_de_friccion.level,
                    1 if item.revision_humana_requerida else 0,
                    item.estado_de_la_puerta_de_supervision_humana.status,
                    item.referencia_de_auditoria,
                    json.dumps(item.model_dump(mode="json", by_alias=True), ensure_ascii=True),
                    item.created_at.isoformat(),
                ),
            )

    def get_case(self, case_id: str) -> ChangeCase | None:
        with get_connection() as connection:
            row = connection.execute("SELECT payload_json FROM change_cases WHERE case_id = ?", (case_id,)).fetchone()
        if row is None:
            return None
        return ChangeCase.model_validate(json.loads(row["payload_json"]))

    def append_audit_event(self, event: AuditEvent) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO audit_events (
                    audit_event_id, reference, entity_type, entity_id, action, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.reference,
                    event.entity_type,
                    event.entity_id,
                    event.action,
                    json.dumps(event.payload, ensure_ascii=True),
                    event.created_at.isoformat(),
                ),
            )

    def audit_events_by_reference(self, reference: str) -> list[AuditEvent]:
        with get_connection() as connection:
            rows = connection.execute("SELECT * FROM audit_events WHERE reference = ? ORDER BY created_at ASC", (reference,)).fetchall()
        return [
            AuditEvent(
                id=row["audit_event_id"],
                reference=row["reference"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                action=row["action"],
                payload=json.loads(row["payload_json"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def health(self) -> dict:
        from core.db.session import check_db_health

        return check_db_health()


def _build_case_store() -> CaseStore:
    if settings.storage_backend == "supabase":
        return SupabaseStore()
    return SqlStore()


def _build_cache_store() -> CacheStore:
    if settings.cache_backend == "upstash":
        return UpstashRedisCache()
    return InMemoryCache()


def _build_vector_store() -> VectorStore:
    if settings.vector_backend == "neon":
        return NeonPgVectorStore()
    return NoopVectorStore()


class StorageRuntime:
    def __init__(self, case_store: CaseStore, cache_store: CacheStore, vector_store: VectorStore) -> None:
        self.case_store = case_store
        self.cache_store = cache_store
        self.vector_store = vector_store
        self.mode = f"case={case_store.mode};cache={cache_store.mode};vector={vector_store.mode}"

    def save_case(self, item: ChangeCase) -> None:
        self.case_store.save_case(item)
        self._safe_cache_set(f"change_case:{item.case_id}", item.model_dump(mode="json"))
        self._safe_vector_index(item)

    def get_case(self, case_id: str) -> ChangeCase | None:
        cached = self.cache_store.get_json(f"change_case:{case_id}")
        if cached is not None:
            return ChangeCase.model_validate(cached)
        item = self.case_store.get_case(case_id)
        if item is not None:
            self._safe_cache_set(f"change_case:{case_id}", item.model_dump(mode="json"))
        return item

    def append_audit_event(self, event: AuditEvent) -> None:
        self.case_store.append_audit_event(event)
        self._safe_cache_set(f"audit:{event.reference}:{event.id}", event.model_dump(mode="json"))

    def audit_events_by_reference(self, reference: str) -> list[AuditEvent]:
        return self.case_store.audit_events_by_reference(reference)

    def health_report(self) -> dict:
        return {
            "case_store": self.case_store.health(),
            "cache_store": self.cache_store.health(),
            "vector_store": self.vector_store.health(),
        }

    def _safe_cache_set(self, key: str, value: dict) -> None:
        try:
            self.cache_store.set_json(key, value)
        except Exception:
            return None

    def _safe_vector_index(self, item: ChangeCase) -> None:
        try:
            self.vector_store.index_case(item)
        except Exception:
            return None


STORE = StorageRuntime(_build_case_store(), _build_cache_store(), _build_vector_store())
