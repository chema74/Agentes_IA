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
    app_name: str = _env("APP_NAME", "asistente-legal-supervisado")
    app_env: str = _env("APP_ENV", "demo")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8050")
    service_api_key: str = _env("SERVICE_API_KEY")
    require_api_key: bool = _env_bool("REQUIRE_API_KEY", True)
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    supabase_url: str = _env("SUPABASE_URL")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    upstash_redis_rest_url: str = _env("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = _env("UPSTASH_REDIS_REST_TOKEN")
    neon_database_url: str = _env("NEON_DATABASE_URL", "sqlite:///./data/autonomous_legal_counsel.sqlite3")
    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-1.5-pro")
    a2a_base_url: str = _env("A2A_BASE_URL")
    enable_fallback_playbooks: bool = _env_bool("ENABLE_FALLBACK_PLAYBOOKS", True)
    enable_fallback_negotiation: bool = _env_bool("ENABLE_FALLBACK_NEGOTIATION", True)
    intake_timeout_seconds: int = int(_env("INTAKE_TIMEOUT_SECONDS", "15"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
