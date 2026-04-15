from __future__ import annotations

try:
    from sqlalchemy.orm import DeclarativeBase
except Exception:  # pragma: no cover
    class DeclarativeBase:  # type: ignore[override]
        pass


class Base(DeclarativeBase):
    pass
