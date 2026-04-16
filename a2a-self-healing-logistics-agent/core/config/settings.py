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
    app_name: str = _env("APP_NAME", "a2a-self-healing-logistics-agent")
    app_env: str = _env("APP_ENV", "demo")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8030")
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    supabase_url: str = _env("SUPABASE_URL")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    upstash_redis_rest_url: str = _env("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = _env("UPSTASH_REDIS_REST_TOKEN")
    neon_database_url: str = _env("NEON_DATABASE_URL", "sqlite:///./data/a2a_self_healing_logistics.sqlite3")
    groq_api_key: str = _env("GROQ_API_KEY")
    groq_model: str = _env("GROQ_MODEL", "llama3-8b-8192")
    a2a_discovery_base_url: str = _env("A2A_DISCOVERY_BASE_URL")
    mcp_broker_url: str = _env("MCP_BROKER_URL")
    a2a_timeout_seconds: int = int(_env("A2A_TIMEOUT_SECONDS", "10"))
    max_negotiation_increment: float = float(_env("MAX_NEGOTIATION_INCREMENT", "0.25"))
    max_incremental_cost_ratio: float = float(_env("MAX_INCREMENTAL_COST_RATIO", "0.35"))
    enable_fallback_discovery: bool = _env_bool("ENABLE_FALLBACK_DISCOVERY", True)
    enable_fallback_negotiation: bool = _env_bool("ENABLE_FALLBACK_NEGOTIATION", True)
    enable_fallback_governance: bool = _env_bool("ENABLE_FALLBACK_GOVERNANCE", True)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
