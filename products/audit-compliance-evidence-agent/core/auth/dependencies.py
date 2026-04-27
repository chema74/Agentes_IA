from __future__ import annotations

from core.auth.supabase_auth import get_user_from_token
from core.security.access import UserContext


def current_user_from_token(token: str | None) -> UserContext:
    user = get_user_from_token(token)
    if user is None:
        raise PermissionError("Unauthenticated request.")
    return user
