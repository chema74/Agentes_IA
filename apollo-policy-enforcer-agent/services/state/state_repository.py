from __future__ import annotations

import httpx

from core.config.settings import settings
from domain.state.models import StateAssertion, SymbolicState


class StateRepository:
    def build_symbolic_state(self, entity_id: str, entity_type: str, context: dict) -> SymbolicState:
        if not settings.enable_fallback_state_store and settings.supabase_url and settings.supabase_service_role_key:
            remote = self._fetch_remote_state(entity_id=entity_id, entity_type=entity_type)
            if remote is not None:
                return remote
        assertions = []
        inconsistencies = []
        for key, value in context.items():
            assertions.append(
                StateAssertion(
                    key=key,
                    value=value,
                    source_of_truth="request_context",
                    freshness_minutes=1,
                )
            )
        if context.get("state_conflict") is True:
            inconsistencies.append("Explicit conflict flag provided in context.")
        return SymbolicState(entity_id=entity_id, entity_type=entity_type, assertions=assertions, inconsistencies_detected=inconsistencies)

    def _fetch_remote_state(self, entity_id: str, entity_type: str) -> SymbolicState | None:
        try:
            with httpx.Client(timeout=settings.intent_typing_timeout_seconds, headers=self._headers()) as client:
                response = client.get(
                    f"{settings.supabase_url}/rest/v1/symbolic_states",
                    params={"entity_id": f"eq.{entity_id}", "entity_type": f"eq.{entity_type}", "limit": "1"},
                )
                response.raise_for_status()
            data = response.json()
            if not data:
                return None
            return SymbolicState.model_validate(data[0])
        except Exception:
            return None

    def _headers(self) -> dict:
        return {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
        }

    def health(self) -> dict:
        if settings.enable_fallback_state_store or not settings.supabase_url or not settings.supabase_service_role_key:
            return {"status": "fallback", "backend": "request-context"}
        try:
            with httpx.Client(timeout=settings.intent_typing_timeout_seconds, headers=self._headers()) as client:
                response = client.get(f"{settings.supabase_url}/rest/v1/symbolic_states", params={"limit": "1"})
                response.raise_for_status()
            return {"status": "ok", "backend": "supabase"}
        except Exception as exc:
            return {"status": "error", "backend": "supabase", "detail": str(exc)}


STATE_REPOSITORY = StateRepository()
