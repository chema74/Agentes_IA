from __future__ import annotations

try:
    from fastapi import FastAPI
except ImportError:
    FastAPI = None

from core.logging.logger import configure_logging

configure_logging()

if FastAPI is not None:
    from app.api.routes import router

    app = FastAPI(title="nspa-psychological-orchestrator", version="0.1.0")
    if router is not None:
        app.include_router(router)
else:
    app = None
