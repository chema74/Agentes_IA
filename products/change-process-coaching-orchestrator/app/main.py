from __future__ import annotations

from fastapi import FastAPI

from app.middleware.rate_limit import InMemoryRateLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.api.routes import router
from core.config.settings import settings
from core.db.session import init_db
from core.logging.logger import configure_logging


configure_logging()
init_db()

app = FastAPI(title="change-process-coaching-orchestrator", version="0.1.0")
app.add_middleware(RequestContextMiddleware)
if settings.enable_rate_limit:
    app.add_middleware(
        InMemoryRateLimitMiddleware,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
app.include_router(router)
