from __future__ import annotations

import json
from dataclasses import dataclass
from threading import Lock

from core.db.session import get_connection, init_db
from domain.audit.models import AuditEvent
from domain.cases.models import TradeCase


@dataclass
class SqlStore:
    mode: str = "sql-backed"

    def __post_init__(self) -> None:
        self._lock = Lock()
        init_db()

    def save_case(self, item: TradeCase) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO trade_cases (
                    case_id, signal_status, international_risk_level, human_review_required,
                    review_gate_status, audit_reference, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.case_id,
                    item.estado_de_la_señal_geopolítica,
                    item.nivel_de_riesgo_internacional,
                    1 if item.revisión_humana_requerida else 0,
                    item.estado_de_la_puerta_de_revisión_humana.status,
                    item.referencia_de_auditoría,
                    json.dumps(item.model_dump(mode="json"), ensure_ascii=True),
                    item.created_at.isoformat(),
                ),
            )

    def get_case(self, case_id: str) -> TradeCase | None:
        with get_connection() as connection:
            row = connection.execute("SELECT payload_json FROM trade_cases WHERE case_id = ?", (case_id,)).fetchone()
        if row is None:
            return None
        return TradeCase.model_validate(json.loads(row["payload_json"]))

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


STORE = SqlStore()
