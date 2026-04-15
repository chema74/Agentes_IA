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
    app_name: str = _env("APP_NAME", "audit-compliance-evidence-agent")
    app_env: str = _env("APP_ENV", "demo")
    app_secret_key: str = _env("APP_SECRET_KEY", "change-me")
    app_base_url: str = _env("APP_BASE_URL", "http://127.0.0.1:8000")
    data_dir: Path = Path(_env("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_env("APP_EXPORT_DIR", "./exports")).resolve()
    db_url: str = _env("DB_URL", "sqlite:///./data/audit_compliance_evidence.sqlite3")
    supabase_url: str = _env("SUPABASE_URL")
    supabase_key: str = _env("SUPABASE_KEY")
    supabase_anon_key: str = _env("SUPABASE_ANON_KEY")
    supabase_service_role_key: str = _env("SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str = _env("SUPABASE_JWT_SECRET")
    supabase_storage_bucket_evidence: str = _env("SUPABASE_STORAGE_BUCKET_EVIDENCE", "evidence-files")
    supabase_storage_bucket_packages: str = _env("SUPABASE_STORAGE_BUCKET_PACKAGES", "audit-packages")
    enable_pgvector: bool = _env_bool("ENABLE_PGVECTOR", False)
    litellm_model: str = _env("LITELLM_MODEL", "groq/llama-3.3-70b-versatile")
    litellm_fallback_model: str = _env("LITELLM_FALLBACK_MODEL", "groq/llama-3.1-8b-instant")
    groq_api_key: str = _env("GROQ_API_KEY")
    openai_api_key: str = _env("OPENAI_API_KEY")
    gemini_api_key: str = _env("GEMINI_API_KEY")
    anthropic_api_key: str = _env("ANTHROPIC_API_KEY")
    redaction_enabled: bool = _env_bool("REDACTION_ENABLED", True)
    max_file_mb: int = int(_env("MAX_FILE_MB", "25"))
    mock_auth_enabled: bool = _env_bool("MOCK_AUTH_ENABLED", True)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
