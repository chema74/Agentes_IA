from __future__ import annotations

import hashlib
import json

try:
    import psycopg
except Exception:  # pragma: no cover
    psycopg = None

from core.config.settings import settings
from domain.cases.models import ChangeCase


class NoopVectorStore:
    mode = "noop-vector"

    def index_case(self, item: ChangeCase) -> None:
        return None

    def health(self) -> dict:
        return {"status": "ok", "backend": self.mode}


class NeonPgVectorStore:
    mode = "neon-pgvector"

    def __init__(self) -> None:
        self._dsn = settings.neon_database_url
        self._dimensions = settings.vector_dimensions

    def _connect(self):
        if psycopg is None:
            raise RuntimeError("psycopg is required for neon/pgvector support")
        return psycopg.connect(self._dsn)

    def _embedding_for_case(self, item: ChangeCase) -> list[float]:
        text = json.dumps(
            {
                "status": item.estado_del_proceso_de_cambio,
                "recommendation": item.recomendacion_final.summary,
                "signals": [signal.summary for signal in item.resumen_de_senales_detectadas],
            },
            ensure_ascii=True,
        )
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for index in range(self._dimensions):
            byte = digest[index % len(digest)]
            values.append(round(byte / 255.0, 6))
        return values

    def _vector_literal(self, values: list[float]) -> str:
        return "[" + ",".join(f"{value:.6f}" for value in values) + "]"

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS change_case_vectors (
                        case_id TEXT PRIMARY KEY,
                        audit_reference TEXT NOT NULL,
                        payload_json JSONB NOT NULL,
                        embedding vector({self._dimensions}) NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            connection.commit()

    def index_case(self, item: ChangeCase) -> None:
        self.ensure_schema()
        embedding = self._vector_literal(self._embedding_for_case(item))
        payload = json.dumps(item.model_dump(mode="json", by_alias=True), ensure_ascii=True)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO change_case_vectors (case_id, audit_reference, payload_json, embedding)
                    VALUES (%s, %s, %s::jsonb, %s::vector)
                    ON CONFLICT (case_id) DO UPDATE SET
                        audit_reference = EXCLUDED.audit_reference,
                        payload_json = EXCLUDED.payload_json,
                        embedding = EXCLUDED.embedding
                    """,
                    (item.case_id, item.referencia_de_auditoria, payload, embedding),
                )
            connection.commit()

    def health(self) -> dict:
        if not self._dsn.startswith(("postgres://", "postgresql://")):
            return {"status": "skipped", "backend": self.mode, "detail": "Neon postgres DSN not configured"}
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return {"status": "ok", "backend": self.mode, "dimensions": self._dimensions}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "backend": self.mode, "detail": str(exc)}
