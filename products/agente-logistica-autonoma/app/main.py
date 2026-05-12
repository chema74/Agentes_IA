from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from core.logging.logger import configure_logging


configure_logging()

app = FastAPI(title="agente-logistica-autonoma", version="0.1.0")
app.include_router(router)
