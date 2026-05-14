from __future__ import annotations

import hmac
import os

from core.config.settings import settings
from core.security.access import UserContext


DEMO_USERS = {
    "compliance@example.com": UserContext(user_id="demo-compliance", email="compliance@example.com", role="compliance"),
    "auditor@example.com": UserContext(user_id="demo-auditor", email="auditor@example.com", role="auditor"),
    "owner@example.com": UserContext(user_id="demo-owner", email="owner@example.com", role="owner"),
}


def authenticate(email: str, password: str) -> UserContext:
    demo_password = os.getenv("DEMO_AUTH_PASSWORD", "").strip()
    if (
        settings.mock_auth_enabled
        and demo_password
        and email in DEMO_USERS
        and hmac.compare_digest(password, demo_password)
    ):
        return DEMO_USERS[email]
    raise PermissionError("Authentication failed.")


def get_user_from_token(token: str | None) -> UserContext | None:
    if settings.mock_auth_enabled and token in {user.user_id for user in DEMO_USERS.values()}:
        return next(user for user in DEMO_USERS.values() if user.user_id == token)
    return None
