from __future__ import annotations

import time
from collections import deque
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def _client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded_for:
            return forwarded_for
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        key = self._client_key(request)
        now = time.time()
        with self._lock:
            bucket = self._hits.setdefault(key, deque())
            while bucket and now - bucket[0] > self.window_seconds:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded",
                        "max_requests": self.max_requests,
                        "window_seconds": self.window_seconds,
                    },
                )
            bucket.append(now)
        return await call_next(request)
