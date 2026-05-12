from __future__ import annotations

import json
from dataclasses import dataclass
from threading import Lock

from core.db.session import get_connection, init_db
from domain.audit.models import AuditEvent
from domain.contracts.models import ContractReview
from domain.negotiation.models import NegotiationTrack


@dataclass
class SqlStore:
    mode: str = "sql-backed"

    def __post_init__(self) -> None:
        self._lock = Lock()
        init_db()

    def save_review(self, review: ContractReview) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO contract_reviews (
                    review_id, contract_type, approval_recommendation, human_review_required,
                    negotiation_status, audit_reference, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review.review_id,
                    review.contract_type,
                    review.approval_recommendation.status,
                    1 if review.human_review_required else 0,
                    review.negotiation_status,
                    review.audit_reference,
                    json.dumps(review.model_dump(mode="json"), ensure_ascii=True),
                    review.created_at.isoformat(),
                ),
            )

    def get_review(self, review_id: str) -> ContractReview | None:
        with get_connection() as connection:
            row = connection.execute("SELECT payload_json FROM contract_reviews WHERE review_id = ?", (review_id,)).fetchone()
        if row is None:
            return None
        return ContractReview.model_validate(json.loads(row["payload_json"] if hasattr(row, "__getitem__") else row["payload_json"]))

    def save_negotiation_track(self, track: NegotiationTrack) -> None:
        with self._lock, get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO negotiation_tracks (
                    track_id, review_id, issue_key, round_number, status, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    track.track_id,
                    track.review_id,
                    track.issue_key,
                    track.round_number,
                    track.status,
                    json.dumps(track.model_dump(mode="json"), ensure_ascii=True),
                    track.created_at.isoformat(),
                ),
            )

    def list_tracks(self, review_id: str) -> list[NegotiationTrack]:
        with get_connection() as connection:
            rows = connection.execute("SELECT payload_json FROM negotiation_tracks WHERE review_id = ? ORDER BY created_at ASC", (review_id,)).fetchall()
        return [NegotiationTrack.model_validate(json.loads(row["payload_json"])) for row in rows]

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
