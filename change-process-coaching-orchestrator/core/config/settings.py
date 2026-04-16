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
    app_name: str = _env("APP_NAME", "change-process-coaching-orchestrator")
    app_env: str = _env("APP_ENV", "demo")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8060")
    service_api_key: str = _env("SERVICE_API_KEY", "change-dev-key")
    require_api_key: bool = _env_bool("REQUIRE_API_KEY", True)
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    storage_backend: str = _env("STORAGE_BACKEND", "local")
    cache_backend: str = _env("CACHE_BACKEND", "memory")
    vector_backend: str = _env("VECTOR_BACKEND", "local")
    supabase_url: str = _env("SUPABASE_URL")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    upstash_redis_rest_url: str = _env("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = _env("UPSTASH_REDIS_REST_TOKEN")
    neon_database_url: str = _env("NEON_DATABASE_URL", "sqlite:///./data/change_process_coaching.sqlite3")
    vector_dimensions: int = int(_env("VECTOR_DIMENSIONS", "8"))
    langsmith_api_key: str = _env("LANGSMITH_API_KEY")
    langsmith_project: str = _env("LANGSMITH_PROJECT", "change-process-coaching")
    groq_api_key: str = _env("GROQ_API_KEY")
    groq_model: str = _env("GROQ_MODEL", "llama3-8b-8192")
    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-1.5-pro")
    enable_gemini_depth: bool = _env_bool("ENABLE_GEMINI_DEPTH", False)
    intake_timeout_seconds: int = int(_env("INTAKE_TIMEOUT_SECONDS", "15"))
    storage_timeout_seconds: int = int(_env("STORAGE_TIMEOUT_SECONDS", "10"))
    storage_retry_attempts: int = int(_env("STORAGE_RETRY_ATTEMPTS", "2"))
    storage_retry_delay_seconds: float = float(_env("STORAGE_RETRY_DELAY_SECONDS", "0.2"))
    enable_rate_limit: bool = _env_bool("ENABLE_RATE_LIMIT", False)
    rate_limit_requests: int = int(_env("RATE_LIMIT_REQUESTS", "60"))
    rate_limit_window_seconds: int = int(_env("RATE_LIMIT_WINDOW_SECONDS", "60"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
