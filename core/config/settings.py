"""
Configuracion compartida del monorepo.

Objetivos:
- cargar variables desde `.env` sin bloquear el import en modo demo
- exponer constantes compatibles con el codigo existente
- dejar la validacion fuerte en funciones explicitas
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, get_args

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on", "si", "sí"}


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _read_env(name: str, default: Any = None) -> Any:
    env_value = os.getenv(name)
    if env_value is not None:
        return env_value

    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    return default


AppMode = Literal["demo", "production"]


@dataclass(frozen=True)
class Settings:
    app_mode: AppMode
    is_demo: bool
    is_production: bool
    groq_api_key: str
    tavily_api_key: str
    model_name: str
    fallback_model_name: str
    enable_llm_fallback: bool
    temperature: float
    max_tokens: int
    request_timeout_seconds: int
    search_depth: str
    max_results_per_query: int
    max_retries: int
    initial_backoff_seconds: float
    backoff_multiplier: float
    max_backoff_seconds: float
    retry_jitter_seconds: float
    throttling_delay: float


def _resolve_app_mode() -> AppMode:
    raw_mode = str(_read_env("APP_MODE", "demo")).strip().lower()
    if raw_mode not in get_args(AppMode):
        return "demo"
    return raw_mode  # type: ignore[return-value]


def build_settings() -> Settings:
    app_mode = _resolve_app_mode()
    is_demo = app_mode == "demo"

    search_depth = str(_read_env("SEARCH_DEPTH", "advanced")).strip().lower()
    if search_depth not in {"basic", "advanced"}:
        search_depth = "advanced"

    model_name = str(_read_env("MODEL_NAME", "llama-3.3-70b-versatile")).strip()
    if not model_name:
        model_name = "llama-3.3-70b-versatile"

    fallback_model_name = str(
        _read_env("FALLBACK_MODEL_NAME", "llama-3.1-8b-instant")
    ).strip()
    enable_llm_fallback = _to_bool(_read_env("ENABLE_LLM_FALLBACK", "true"))
    if enable_llm_fallback and not fallback_model_name:
        fallback_model_name = "llama-3.1-8b-instant"

    max_results_per_query = max(1, _to_int(_read_env("MAX_RESULTS_PER_QUERY", 5), 5))
    max_tokens = max(1, _to_int(_read_env("MAX_TOKENS", 1800), 1800))
    request_timeout_seconds = max(
        1, _to_int(_read_env("REQUEST_TIMEOUT_SECONDS", 45), 45)
    )

    return Settings(
        app_mode=app_mode,
        is_demo=is_demo,
        is_production=not is_demo,
        groq_api_key=str(_read_env("GROQ_API_KEY", "")).strip(),
        tavily_api_key=str(_read_env("TAVILY_API_KEY", "")).strip(),
        model_name=model_name,
        fallback_model_name=fallback_model_name,
        enable_llm_fallback=enable_llm_fallback,
        temperature=_to_float(_read_env("TEMPERATURE", 0.2), 0.2),
        max_tokens=max_tokens,
        request_timeout_seconds=request_timeout_seconds,
        search_depth=search_depth,
        max_results_per_query=max_results_per_query,
        max_retries=max(1, _to_int(_read_env("MAX_RETRIES", 4), 4)),
        initial_backoff_seconds=max(
            0.0, _to_float(_read_env("INITIAL_BACKOFF_SECONDS", 1.5), 1.5)
        ),
        backoff_multiplier=max(
            1.0, _to_float(_read_env("BACKOFF_MULTIPLIER", 2.0), 2.0)
        ),
        max_backoff_seconds=max(
            0.0, _to_float(_read_env("MAX_BACKOFF_SECONDS", 20.0), 20.0)
        ),
        retry_jitter_seconds=max(
            0.0, _to_float(_read_env("RETRY_JITTER_SECONDS", 0.3), 0.3)
        ),
        throttling_delay=max(0.0, _to_float(_read_env("THROTTLING_DELAY", 0.8), 0.8)),
    )


def get_settings() -> Settings:
    return build_settings()


def missing_required_api_keys(settings: Settings | None = None) -> list[str]:
    settings = settings or get_settings()
    if settings.is_demo:
        return []

    missing: list[str] = []
    if not settings.groq_api_key:
        missing.append("GROQ_API_KEY")
    if not settings.tavily_api_key:
        missing.append("TAVILY_API_KEY")
    return missing


def validate_runtime_configuration(settings: Settings | None = None) -> list[str]:
    settings = settings or get_settings()
    return missing_required_api_keys(settings)


def validate_api_configuration(settings: Settings | None = None) -> None:
    missing = validate_runtime_configuration(settings)
    if missing:
        raise RuntimeError(
            "Faltan variables de entorno obligatorias: " + ", ".join(missing)
        )


validar_configuracion_runtime = validate_runtime_configuration
validar_configuracion_api = validate_api_configuration


_SETTINGS = get_settings()

APP_MODE = _SETTINGS.app_mode
IS_DEMO = _SETTINGS.is_demo
IS_PRODUCTION = _SETTINGS.is_production
GROQ_API_KEY = _SETTINGS.groq_api_key
TAVILY_API_KEY = _SETTINGS.tavily_api_key
MODEL_NAME = _SETTINGS.model_name
FALLBACK_MODEL_NAME = _SETTINGS.fallback_model_name
ENABLE_LLM_FALLBACK = _SETTINGS.enable_llm_fallback
TEMPERATURE = _SETTINGS.temperature
MAX_TOKENS = _SETTINGS.max_tokens
REQUEST_TIMEOUT_SECONDS = _SETTINGS.request_timeout_seconds
SEARCH_DEPTH = _SETTINGS.search_depth
MAX_RESULTS_PER_QUERY = _SETTINGS.max_results_per_query
MAX_RETRIES = _SETTINGS.max_retries
INITIAL_BACKOFF_SECONDS = _SETTINGS.initial_backoff_seconds
BACKOFF_MULTIPLIER = _SETTINGS.backoff_multiplier
MAX_BACKOFF_SECONDS = _SETTINGS.max_backoff_seconds
RETRY_JITTER_SECONDS = _SETTINGS.retry_jitter_seconds
THROTTLING_DELAY = _SETTINGS.throttling_delay


__all__ = [
    "PROJECT_ROOT",
    "ENV_FILE",
    "Settings",
    "get_settings",
    "build_settings",
    "missing_required_api_keys",
    "validate_runtime_configuration",
    "validate_api_configuration",
    "validar_configuracion_runtime",
    "validar_configuracion_api",
    "APP_MODE",
    "IS_DEMO",
    "IS_PRODUCTION",
    "GROQ_API_KEY",
    "TAVILY_API_KEY",
    "MODEL_NAME",
    "FALLBACK_MODEL_NAME",
    "ENABLE_LLM_FALLBACK",
    "TEMPERATURE",
    "MAX_TOKENS",
    "REQUEST_TIMEOUT_SECONDS",
    "SEARCH_DEPTH",
    "MAX_RESULTS_PER_QUERY",
    "MAX_RETRIES",
    "INITIAL_BACKOFF_SECONDS",
    "BACKOFF_MULTIPLIER",
    "MAX_BACKOFF_SECONDS",
    "RETRY_JITTER_SECONDS",
    "THROTTLING_DELAY",
]
