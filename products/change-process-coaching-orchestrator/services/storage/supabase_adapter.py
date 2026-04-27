from __future__ import annotations

import json
import time
from collections.abc import Callable

import httpx

from core.config.settings import settings
from domain.audit.models import AuditEvent
from domain.cases.models import ChangeCase


class SupabaseStore:
    mode = "supabase-rest"

    def __init__(self) -> None:
        self._base_url = settings.supabase_url.rstrip("/")
        self._timeout = settings.storage_timeout_seconds
        self._retry_attempts = settings.storage_retry_attempts
        self._retry_delay = settings.storage_retry_delay_seconds

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates",
        }

    def _endpoint(self, table: str) -> str:
        return f"{self._base_url}/rest/v1/{table}"

    def _request(self, operation: Callable[[], httpx.Response]) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, self._retry_attempts + 1):
            try:
                response = operation()
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code < 500 or attempt == self._retry_attempts:
                    raise
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                if attempt == self._retry_attempts:
                    raise
            time.sleep(self._retry_delay * attempt)
        if last_error is not None:
            raise last_error
        raise RuntimeError("Supabase request failed without explicit error")

    def save_case(self, item: ChangeCase) -> None:
        payload = {
            "case_id": item.case_id,
            "process_status": item.estado_del_proceso_de_cambio,
            "friction_level": item.nivel_de_friccion.level,
            "human_review_required": item.revision_humana_requerida,
            "supervision_gate_status": item.estado_de_la_puerta_de_supervision_humana.status,
            "audit_reference": item.referencia_de_auditoria,
            "payload_json": json.dumps(item.model_dump(mode="json", by_alias=True), ensure_ascii=True),
            "created_at": item.created_at.isoformat(),
        }
        with httpx.Client(timeout=self._timeout) as client:
            self._request(
                lambda: client.post(self._endpoint("change_cases"), headers=self._headers(), params={"on_conflict": "case_id"}, json=payload)
            )

    def get_case(self, case_id: str) -> ChangeCase | None:
        with httpx.Client(timeout=self._timeout) as client:
            response = self._request(
                lambda: client.get(
                    self._endpoint("change_cases"),
                    headers=self._headers(),
                    params={"case_id": f"eq.{case_id}", "select": "payload_json", "limit": "1"},
                )
            )
        rows = response.json()
        if not rows:
            return None
        return ChangeCase.model_validate(json.loads(rows[0]["payload_json"]))

    def append_audit_event(self, event: AuditEvent) -> None:
        payload = {
            "audit_event_id": event.id,
            "reference": event.reference,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "action": event.action,
            "payload_json": json.dumps(event.payload, ensure_ascii=True),
            "created_at": str(event.created_at),
        }
        with httpx.Client(timeout=self._timeout) as client:
            self._request(
                lambda: client.post(self._endpoint("audit_events"), headers=self._headers(), params={"on_conflict": "audit_event_id"}, json=payload)
            )

    def audit_events_by_reference(self, reference: str) -> list[AuditEvent]:
        with httpx.Client(timeout=self._timeout) as client:
            response = self._request(
                lambda: client.get(
                    self._endpoint("audit_events"),
                    headers=self._headers(),
                    params={"reference": f"eq.{reference}", "select": "*", "order": "created_at.asc"},
                )
            )
        rows = response.json()
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
        if not settings.supabase_url or not settings.supabase_service_role_key:
            return {"status": "skipped", "backend": self.mode, "detail": "Supabase credentials not configured"}
        try:
            with httpx.Client(timeout=self._timeout) as client:
                self._request(lambda: client.get(self._endpoint("change_cases"), headers=self._headers(), params={"select": "case_id", "limit": "1"}))
            return {"status": "ok", "backend": self.mode}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "backend": self.mode, "detail": str(exc)}
