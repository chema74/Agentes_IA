from __future__ import annotations

import json
from dataclasses import dataclass, field
from threading import Lock

from core.db.session import get_connection, init_db
from domain.audit.models import AuditEvent
from domain.mandates.models import ActionMandate
from domain.policies.models import PolicyRule
from domain.validation.models import ValidationTrace


@dataclass
class SqlStore:
    mode: str = "sql-backed"
    policies: dict[str, PolicyRule] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._lock = Lock()
        init_db()

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
            rows = connection.execute(
                "SELECT * FROM audit_events WHERE reference = ? ORDER BY created_at ASC",
                (reference,),
            ).fetchall()
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

    def save_mandate(self, mandate: ActionMandate, idempotency_key: str | None = None) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO action_mandates (
                    mandate_id, actor_id, target_resource, decision, audit_reference,
                    typed_intent_json, constraints_applied_json, explanation, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mandate.mandate_id,
                    mandate.actor_id,
                    mandate.target_resource,
                    mandate.decision,
                    mandate.audit_reference,
                    json.dumps(mandate.typed_intent.model_dump(mode="json"), ensure_ascii=True),
                    json.dumps(mandate.constraints_applied, ensure_ascii=True),
                    mandate.explanation,
                    mandate.created_at.isoformat(),
                ),
            )
            if idempotency_key:
                response_json = json.dumps(mandate.model_dump(mode="json"), ensure_ascii=True)
                connection.execute(
                    """
                    INSERT OR REPLACE INTO idempotency_keys (
                        idempotency_key, mandate_id, response_json, created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (idempotency_key, mandate.mandate_id, response_json, mandate.created_at.isoformat()),
                )

    def get_mandate(self, mandate_id: str) -> ActionMandate | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM action_mandates WHERE mandate_id = ?",
                (mandate_id,),
            ).fetchone()
        if row is None:
            return None
        return ActionMandate.model_validate(
            {
                "mandate_id": row["mandate_id"],
                "actor_id": row["actor_id"],
                "target_resource": row["target_resource"],
                "decision": row["decision"],
                "audit_reference": row["audit_reference"],
                "typed_intent": json.loads(row["typed_intent_json"]),
                "constraints_applied": json.loads(row["constraints_applied_json"]),
                "explanation": row["explanation"],
                "created_at": row["created_at"],
            }
        )

    def save_trace(self, trace: ValidationTrace) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO validation_traces (
                    trace_id, intent_id, policy_ids_json, state_assertions_used_json,
                    decision_path_json, evaluated_predicates_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace.trace_id,
                    trace.intent_id,
                    json.dumps(trace.policy_ids, ensure_ascii=True),
                    json.dumps(trace.state_assertions_used, ensure_ascii=True),
                    json.dumps(trace.decision_path, ensure_ascii=True),
                    json.dumps([item.model_dump(mode="json") for item in trace.evaluated_predicates], ensure_ascii=True),
                    trace.created_at.isoformat(),
                ),
            )

    def get_trace_by_intent_id(self, intent_id: str) -> ValidationTrace | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM validation_traces WHERE intent_id = ? ORDER BY created_at DESC LIMIT 1",
                (intent_id,),
            ).fetchone()
        if row is None:
            return None
        return ValidationTrace.model_validate(
            {
                "trace_id": row["trace_id"],
                "intent_id": row["intent_id"],
                "policy_ids": json.loads(row["policy_ids_json"]),
                "state_assertions_used": json.loads(row["state_assertions_used_json"]),
                "decision_path": json.loads(row["decision_path_json"]),
                "evaluated_predicates": json.loads(row["evaluated_predicates_json"]),
                "created_at": row["created_at"],
            }
        )

    def get_idempotent_response(self, idempotency_key: str | None) -> dict | None:
        if not idempotency_key:
            return None
        with get_connection() as connection:
            row = connection.execute(
                "SELECT response_json FROM idempotency_keys WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row["response_json"])

    def save_idempotent_response(self, idempotency_key: str | None, response_payload: dict) -> None:
        if not idempotency_key:
            return
        mandate_id = response_payload["action_mandate"]["mandate_id"]
        created_at = response_payload["action_mandate"]["created_at"]
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO idempotency_keys (
                    idempotency_key, mandate_id, response_json, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (idempotency_key, mandate_id, json.dumps(response_payload, ensure_ascii=True), created_at),
            )


STORE = SqlStore()
