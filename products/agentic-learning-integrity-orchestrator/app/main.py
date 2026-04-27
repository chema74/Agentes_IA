from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from core.logging.logger import configure_logging

configure_logging()

app = FastAPI(title="agentic-learning-integrity-orchestrator", version="0.1.0")
app.include_router(router)
