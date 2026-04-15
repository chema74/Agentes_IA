from __future__ import annotations

from fastapi import Response


SESSION_COOKIE_NAME = "session_token"


def set_session_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(SESSION_COOKIE_NAME, access_token, httponly=True, samesite="lax")


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME)
