from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from core.db.session import init_db
from core.logging.logger import configure_logging


configure_logging()
init_db()

app = FastAPI(title="agente-cumplimiento-politicas", version="0.1.0")
app.include_router(router)
