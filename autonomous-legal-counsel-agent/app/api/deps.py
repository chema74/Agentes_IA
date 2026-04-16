from __future__ import annotations

from fastapi import Header, HTTPException

from core.config.settings import settings


def require_service_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not settings.require_api_key:
        return "auth-disabled"
    if x_api_key != settings.service_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
