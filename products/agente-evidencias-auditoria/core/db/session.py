from __future__ import annotations

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except Exception:  # pragma: no cover
    create_engine = None  # type: ignore
    sessionmaker = None  # type: ignore

from core.config.settings import settings
from core.db.base import Base


engine = create_engine(settings.db_url, future=True) if create_engine else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True) if sessionmaker and engine else None


def init_db() -> None:
    if engine is None:
        return
    Base.metadata.create_all(bind=engine)
