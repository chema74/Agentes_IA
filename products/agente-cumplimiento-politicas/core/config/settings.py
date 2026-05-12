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
    app_name: str = _env("APP_NAME", "agente-cumplimiento-politicas")
    app_env: str = _env("APP_ENV", "demo")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8040")
    service_api_key: str = _env("SERVICE_API_KEY", "apollo-dev-key")
    require_api_key: bool = _env_bool("REQUIRE_API_KEY", True)
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    supabase_url: str = _env("SUPABASE_URL")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    upstash_redis_rest_url: str = _env("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = _env("UPSTASH_REDIS_REST_TOKEN")
    neon_database_url: str = _env("NEON_DATABASE_URL", "sqlite:///./data/apollo_policy_enforcer.sqlite3")
    sambanova_api_key: str = _env("SAMBANOVA_API_KEY")
    sambanova_model: str = _env("SAMBANOVA_MODEL", "Meta-Llama-3.1-8B-Instruct")
    intent_typing_timeout_seconds: int = int(_env("INTENT_TYPING_TIMEOUT_SECONDS", "10"))
    predicate_cache_ttl_seconds: int = int(_env("PREDICATE_CACHE_TTL_SECONDS", "300"))
    enable_fallback_policy_store: bool = _env_bool("ENABLE_FALLBACK_POLICY_STORE", True)
    enable_fallback_state_store: bool = _env_bool("ENABLE_FALLBACK_STATE_STORE", True)
    enable_fallback_audit_store: bool = _env_bool("ENABLE_FALLBACK_AUDIT_STORE", True)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
