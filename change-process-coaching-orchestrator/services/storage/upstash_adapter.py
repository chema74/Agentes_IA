from __future__ import annotations

import json
import time

import httpx

from core.config.settings import settings


class InMemoryCache:
    mode = "memory"

    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    def set_json(self, key: str, value: dict) -> None:
        self._items[key] = value

    def get_json(self, key: str) -> dict | None:
        return self._items.get(key)

    def health(self) -> dict:
        return {"status": "ok", "backend": self.mode}


class UpstashRedisCache:
    mode = "upstash-redis-rest"

    def __init__(self) -> None:
        self._base_url = settings.upstash_redis_rest_url.rstrip("/")
        self._timeout = settings.storage_timeout_seconds
        self._retry_attempts = settings.storage_retry_attempts
        self._retry_delay = settings.storage_retry_delay_seconds

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.upstash_redis_rest_token}",
            "Content-Type": "application/json",
        }

    def _execute(self, command: list[str]) -> dict:
        last_error: Exception | None = None
        for attempt in range(1, self._retry_attempts + 1):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(self._base_url, headers=self._headers(), content=json.dumps(command))
                    response.raise_for_status()
                return response.json()
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
        raise RuntimeError("Upstash command failed without explicit error")

    def set_json(self, key: str, value: dict) -> None:
        self._execute(["SET", key, json.dumps(value, ensure_ascii=True)])

    def get_json(self, key: str) -> dict | None:
        payload = self._execute(["GET", key])
        value = payload.get("result")
        if value is None:
            return None
        return json.loads(value)

    def health(self) -> dict:
        if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
            return {"status": "skipped", "backend": self.mode, "detail": "Upstash credentials not configured"}
        try:
            payload = self._execute(["PING"])
            return {"status": "ok", "backend": self.mode, "result": payload.get("result", "PONG")}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "backend": self.mode, "detail": str(exc)}
