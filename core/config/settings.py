"""
core/config/settings.py

Responsabilidad:
- centralizar configuración de la aplicación (variables de entorno, etc.)
- cargar variables desde .env
- exponer constantes seguras y compatibles con módulos
- aplicar fail-fast en producción cuando falten claves críticas
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, Literal, get_args

from dotenv import load_dotenv


# ===========================================================
# 1. Rutas Base
# ===========================================================

# Asume que este archivo está en core/config, y la raíz del proyecto es 2 niveles arriba
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True) # Siempre sobreescribir con .env del proyecto


# ===========================================================
# 2. Helpers para Variables de Entorno
# ===========================================================

def _to_bool(value: Any, default: bool = False) -> bool:
    """Convierte distintos formatos habituales a booleano."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on", "si", "sí"}


def _to_int(value: Any, default: int) -> int:
    """Convierte a entero con fallback seguro."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    """Convierte a float con fallback seguro."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _read_env(name: str, default: Any = None) -> Any:
    """
    Lee una variable de entorno con fallback opcional a `st.secrets`
    para compatibilidad con Streamlit Cloud.
    """
    env_value = os.getenv(name)
    if env_value is not None:
        return env_value

    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass # No estamos en un entorno Streamlit o st.secrets no existe

    return default


def _require_env(name: str) -> str:
    """Exige que exista una variable de entorno no vacía."""
    value = _read_env(name)
    if value is None or not str(value).strip():
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria '{name}'."
        )
    return str(value).strip()


# ===========================================================
# 3. Modo de Ejecución (Demo vs Producción)
# ===========================================================

AppMode = Literal["demo", "production"]
APP_MODE: AppMode = str(_read_env("APP_MODE", "demo")).strip().lower() # type: ignore
if APP_MODE not in get_args(AppMode):
    APP_MODE = "demo"

IS_DEMO = APP_MODE == "demo"
IS_PRODUCTION = APP_MODE == "production"

# ===========================================================
# 4. Configuración de API Keys (Centralizada)
# ===========================================================

# En producción, exigimos que las claves existan. En demo, pueden estar vacías.
if IS_PRODUCTION:
    GROQ_API_KEY = _require_env("GROQ_API_KEY")
    TAVILY_API_KEY = _require_env("TAVILY_API_KEY")
else:
    GROQ_API_KEY = str(_read_env("GROQ_API_KEY", "")).strip()
    TAVILY_API_KEY = str(_read_env("TAVILY_API_KEY", "")).strip()

# ===========================================================
# 5. Configuración General LLM
# ===========================================================

MODEL_NAME = str(_read_env("MODEL_NAME", "llama-3.3-70b-versatile")).strip()
FALLBACK_MODEL_NAME = str(
    _read_env("FALLBACK_MODEL_NAME", "llama-3.1-8b-instant")
).strip()
ENABLE_LLM_FALLBACK = _to_bool(_read_env("ENABLE_LLM_FALLBACK", "true"))
TEMPERATURE = _to_float(_read_env("TEMPERATURE", 0.2), 0.2)
MAX_TOKENS = _to_int(_read_env("MAX_TOKENS", 1800), 1800)
REQUEST_TIMEOUT_SECONDS = _to_int(_read_env("REQUEST_TIMEOUT_SECONDS", 45), 45)


# ===========================================================
# 6. Configuración de Búsqueda
# ===========================================================

SEARCH_DEPTH = str(_read_env("SEARCH_DEPTH", "advanced")).strip().lower()
if SEARCH_DEPTH not in {"basic", "advanced"}:
    SEARCH_DEPTH = "advanced"
MAX_RESULTS_PER_QUERY = _to_int(_read_env("MAX_RESULTS_PER_QUERY", 5), 5)

# ===========================================================
# 7. Configuración de Reintentos (Retry)
# ===========================================================

MAX_RETRIES = _to_int(_read_env("MAX_RETRIES", 4), 4)
INITIAL_BACKOFF_SECONDS = _to_float(_read_env("INITIAL_BACKOFF_SECONDS", 1.5), 1.5)
BACKOFF_MULTIPLIER = _to_float(_read_env("BACKOFF_MULTIPLIER", 2.0), 2.0)
MAX_BACKOFF_SECONDS = _to_float(_read_env("MAX_BACKOFF_SECONDS", 20.0), 20.0)
RETRY_JITTER_SECONDS = _to_float(_read_env("RETRY_JITTER_SECONDS", 0.3), 0.3)
THROTTLING_DELAY = _to_float(_read_env("THROTTLING_DELAY", 0.8), 0.8)


# ===========================================================
# 8. Validaciones Finales
# ===========================================================

if not MODEL_NAME:
    raise RuntimeError("MODEL_NAME no puede estar vacío.")

if ENABLE_LLM_FALLBACK and not FALLBACK_MODEL_NAME:
    raise RuntimeError(
        "ENABLE_LLM_FALLBACK=True pero FALLBACK_MODEL_NAME está vacío."
    )

if MAX_RESULTS_PER_QUERY <= 0:
    raise RuntimeError("MAX_RESULTS_PER_QUERY debe ser mayor que 0.")

if MAX_TOKENS <= 0:
    raise RuntimeError("MAX_TOKENS debe ser mayor que 0.")

if REQUEST_TIMEOUT_SECONDS <= 0:
    raise RuntimeError("REQUEST_TIMEOUT_SECONDS debe ser mayor que 0.")


# ===========================================================
# 9. Exports
# ===========================================================

__all__ = [
    "PROJECT_ROOT",
    "ENV_FILE",
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
