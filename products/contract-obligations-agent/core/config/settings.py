from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _get_bool(name: str, default: bool = False) -> bool:
    return _get(name, "true" if default else "false").lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = _get("APP_NAME", "contract-obligations-agent")
    app_env: str = _get("APP_ENV", "demo")
    data_dir: Path = Path(_get("APP_DATA_DIR", "./data")).resolve()
    export_dir: Path = Path(_get("APP_EXPORT_DIR", "./exports")).resolve()
    db_url: str = _get("DB_URL", "sqlite:///./data/contract_obligations.sqlite3")
    vectorstore_backend: str = _get("VECTORSTORE_BACKEND", "chroma")
    chroma_path: Path = Path(_get("CHROMA_PATH", "./data/chroma")).resolve()
    qdrant_url: str = _get("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = _get("QDRANT_COLLECTION", "contract-obligations")
    postgres_url: str = _get("POSTGRES_URL", "postgresql+psycopg://contract_obligations:contract_obligations@localhost:5432/contract_obligations")
    object_storage_backend: str = _get("OBJECT_STORAGE_BACKEND", "local")
    object_storage_endpoint: str = _get("OBJECT_STORAGE_ENDPOINT", "")
    object_storage_bucket: str = _get("OBJECT_STORAGE_BUCKET", "contract-obligations")
    object_storage_prefix: str = _get("OBJECT_STORAGE_PREFIX", "analysis")
    litellm_model: str = _get("LITELLM_MODEL", "groq/llama-3.3-70b-versatile")
    litellm_fallback_model: str = _get("LITELLM_FALLBACK_MODEL", "groq/llama-3.1-8b-instant")
    groq_api_key: str = _get("GROQ_API_KEY")
    openai_api_key: str = _get("OPENAI_API_KEY")
    gemini_api_key: str = _get("GEMINI_API_KEY")
    anthropic_api_key: str = _get("ANTHROPIC_API_KEY")
    max_file_mb: int = int(_get("MAX_FILE_MB", "25"))
    redaction_enabled: bool = _get_bool("REDACTION_ENABLED", True)
    human_review_high_risk: bool = _get_bool("HUMAN_REVIEW_HIGH_RISK", True)

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
