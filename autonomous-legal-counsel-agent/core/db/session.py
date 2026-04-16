from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from core.config.settings import settings

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover
    psycopg = None
    dict_row = None


class DatabaseConnection:
    def __init__(self, connection, backend: str) -> None:
        self._connection = connection
        self.backend = backend

    def execute(self, sql: str, params: tuple = ()):
        statement = sql if self.backend == "sqlite" else sql.replace("?", "%s")
        return self._connection.execute(statement, params)

    def executescript(self, script: str) -> None:
        if self.backend == "sqlite":
            self._connection.executescript(script)
            return
        for statement in [chunk.strip() for chunk in script.split(";") if chunk.strip()]:
            self._connection.execute(statement)

    def commit(self) -> None:
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()


def database_backend() -> str:
    return "postgres" if settings.neon_database_url.startswith(("postgres://", "postgresql://")) else "sqlite"


def _resolve_sqlite_path() -> Path:
    if settings.neon_database_url.startswith("sqlite:///"):
        return Path(settings.neon_database_url.replace("sqlite:///", "", 1)).resolve()
    return (settings.data_dir / "autonomous_legal_counsel.sqlite3").resolve()


DB_PATH = _resolve_sqlite_path()


def init_db() -> None:
    schema_path = Path(__file__).resolve().parent / "sql" / "001_init_schema.sql"
    with get_connection() as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.commit()


@contextmanager
def get_connection():
    backend = database_backend()
    if backend == "postgres":
        if psycopg is None:
            raise RuntimeError("psycopg is required for postgres/neon")
        raw = psycopg.connect(settings.neon_database_url, row_factory=dict_row)
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        raw = sqlite3.connect(DB_PATH)
        raw.row_factory = sqlite3.Row
    connection = DatabaseConnection(raw, backend)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def check_db_health() -> dict:
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
        return {"status": "ok", "backend": database_backend()}
    except Exception as exc:  # pragma: no cover
        return {"status": "error", "backend": database_backend(), "detail": str(exc)}
