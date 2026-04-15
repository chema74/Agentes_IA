from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_bool(name: str, default: bool = False) -> bool:
    return _env(name, "true" if default else "false").lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = _env("APP_NAME", "nspa-psychological-orchestrator")
    app_env: str = _env("APP_ENV", "demo")
    app_secret_key: str = _env("APP_SECRET_KEY", "change-me")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8010")
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    supabase_url: str = _env("SUPABASE_URL")
    supabase_key: str = _env("SUPABASE_KEY")
    supabase_anon_key: str = _env("SUPABASE_ANON_KEY")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str = _env("SUPABASE_JWT_SECRET")
    upstash_redis_rest_url: str = _env("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = _env("UPSTASH_REDIS_REST_TOKEN")
    neon_database_url: str = _env("NEON_DATABASE_URL", "sqlite:///./data/nspa_psychological_orchestrator.sqlite3")
    pgvector_collection: str = _env("PGVECTOR_COLLECTION", "psychological_memory")
    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-1.5-flash")
    enable_mock_auth: bool = _env_bool("ENABLE_MOCK_AUTH", True)
    enable_embeddings: bool = _env_bool("ENABLE_EMBEDDINGS", False)
    max_memory_results: int = int(_env("MAX_MEMORY_RESULTS", "5"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
