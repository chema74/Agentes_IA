from __future__ import annotations

from fastapi import Header, HTTPException, status

from core.auth.dependencies import current_user_from_token


def get_current_user(authorization: str | None = Header(default=None)):
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    try:
        return current_user_from_token(token)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
