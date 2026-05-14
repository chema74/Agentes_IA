from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_auth import router as auth_router
from app.api.routes_controls import router as controls_router
from app.api.routes_evidence import router as evidence_router
from app.api.routes_findings import router as findings_router
from app.api.routes_packages import router as packages_router
from app.api.routes_remediation import router as remediation_router
from app.api.routes_scopes import router as scopes_router
from app.api.routes_workflows import router as workflows_router
from app.web.routes import router as web_router
from core.config.settings import settings
from core.db.session import init_db
from core.logging.logger import configure_logging


configure_logging()
init_db()

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.exception_handler(PermissionError)
async def permission_error_handler(_: Request, exc: PermissionError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


STATIC_DIR = Path(__file__).resolve().parent / "web" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(auth_router)
app.include_router(scopes_router)
app.include_router(controls_router)
app.include_router(evidence_router)
app.include_router(findings_router)
app.include_router(packages_router)
app.include_router(remediation_router)
app.include_router(workflows_router)
app.include_router(web_router)
