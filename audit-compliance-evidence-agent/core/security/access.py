from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserContext:
    user_id: str
    email: str
    role: str


def require_role(user: UserContext, allowed_roles: set[str]) -> None:
    if user.role not in allowed_roles:
        raise PermissionError(f"Role {user.role} is not allowed for this operation.")
