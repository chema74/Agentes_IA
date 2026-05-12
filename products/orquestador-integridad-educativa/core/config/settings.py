from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    app_name: str = _env("APP_NAME", "orquestador-integridad-educativa")
    app_env: str = _env("APP_ENV", "demo")
    app_secret_key: str = _env("APP_SECRET_KEY", "change-me")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8020")
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    supabase_url: str = _env("SUPABASE_URL")
    supabase_key: str = _env("SUPABASE_KEY")
    supabase_anon_key: str = _env("SUPABASE_ANON_KEY")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str = _env("SUPABASE_JWT_SECRET")
    upstash_redis_rest_url: str = _env("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = _env("UPSTASH_REDIS_REST_TOKEN")
    neon_database_url: str = _env("NEON_DATABASE_URL")
    pgvector_collection: str = _env("PGVECTOR_COLLECTION", "learning_integrity_memory")
    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-1.5-pro")
    langsmith_api_key: str = _env("LANGSMITH_API_KEY")
    langsmith_project: str = _env("LANGSMITH_PROJECT", "learning-integrity-demo")
    enable_mock_connectors: bool = _env("ENABLE_MOCK_CONNECTORS", "true").lower() in {"1", "true", "yes", "on"}
    max_memory_results: int = int(_env("MAX_MEMORY_RESULTS", "5"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
