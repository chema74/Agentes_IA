from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserContext:
    user_id: str
    email: str
    role: str


def require_role(
    user: UserContext,
    allowed_roles: set[str] | str,
    *extra_roles: str,
) -> None:
    """
    Valida que el usuario tenga uno de los roles permitidos.

    Acepta dos formas de uso para mantener compatibilidad:

    - require_role(user, {"compliance", "auditor", "owner"})
    - require_role(user, "compliance", "auditor", "owner")
    """
    if extra_roles:
        roles = {str(allowed_roles), *extra_roles}
    elif isinstance(allowed_roles, set):
        roles = allowed_roles
    else:
        roles = {allowed_roles}

    if user.role not in roles:
        raise PermissionError(f"Role {user.role} is not allowed for this operation.")