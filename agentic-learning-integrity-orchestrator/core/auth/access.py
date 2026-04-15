from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserContext:
    user_id: str
    role: str


def require_role(user: UserContext, *roles: str) -> UserContext:
    if user.role not in roles:
        raise PermissionError("Rol no autorizado para esta operacion.")
    return user
