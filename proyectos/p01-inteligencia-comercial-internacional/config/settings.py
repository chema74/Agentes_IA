from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any, Dict, List

import yaml
# from dotenv import load_dotenv # Ya no es necesario aquí
from core.config import settings as core_settings # Importar las settings centrales


# ============================================================
# 1. RUTAS BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
ENV_FILE = BASE_DIR / ".env" # Mantener para compatibilidad si se usa localmente
WEIGHTS_FILE = CONFIG_DIR / "weights.yaml"


# ============================================================
# 2. CARGA DEL .env
# ============================================================

# load_dotenv(dotenv_path=ENV_FILE, override=False) # La carga se hace en core_settings


# ============================================================
# 3. HELPERS
# ============================================================

# Estos helpers se obtienen de core/config/settings.py
_to_bool = core_settings._to_bool
_to_int = core_settings._to_int
_to_float = core_settings._to_float
_read_env = core_settings._read_env
_require_env = core_settings._require_env

def _load_yaml_file(path: Path) -> Dict[str, Any]:
    """
    Carga un archivo YAML de forma segura.
    """
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise RuntimeError(f"El archivo YAML no contiene un objeto válido: {path}")

    return data


def _as_clean_str_list(value: Any) -> List[str]:
    """
    Convierte un valor a lista limpia de strings.
    """
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


def _as_float_dict(value: Any) -> Dict[str, float]:
    """
    Convierte un dict arbitrario a dict[str, float], ignorando entradas inválidas.
    """
    if not isinstance(value, dict):
        return {}

    resultado: Dict[str, float] = {}

    for k, v in value.items():
        key = str(k).strip()
        if not key:
            continue

        try:
            resultado[key] = float(v)
        except (TypeError, ValueError):
            continue

    return resultado


def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normaliza un diccionario de pesos para que sumen 1.0.
    Si no se puede, devuelve el original.
    """
    total = sum(weights.values())
    if total <= 0:
        return weights
    return {k: v / total for k, v in weights.items()}


# ============================================================
# 4. MODO DE EJECUCIÓN
# ============================================================

# Ahora se obtiene de las settings centrales
APP_MODE = core_settings.APP_MODE
IS_DEMO = core_settings.IS_DEMO
IS_PRODUCTION = core_settings.IS_PRODUCTION


# ============================================================
# 5. CONFIGURACIÓN GENERAL
# ============================================================

APP_TITLE = str(
    _read_env("APP_TITLE", "Inteligencia Comercial Internacional")
).strip()
APP_STORAGE_DIR = Path(
    str(_read_env("APP_STORAGE_DIR", BASE_DIR))
).resolve()
HISTORY_BASE_DIR = Path(
    str(_read_env("HISTORY_BASE_DIR", APP_STORAGE_DIR / "history"))
).resolve()
HISTORY_DB_PATH = Path(
    str(_read_env("HISTORY_DB_PATH", APP_STORAGE_DIR / "data" / "p01_history.sqlite3"))
).resolve()
LOGS_DIR = Path(
    str(_read_env("LOGS_DIR", APP_STORAGE_DIR / "logs"))
).resolve()
CACHE_BASE_DIR = Path(
    str(_read_env("CACHE_BASE_DIR", APP_STORAGE_DIR / "outputs" / "cache" / "country_analysis"))
).resolve()

DEBUG_MODE = _to_bool(_read_env("DEBUG_MODE", "true" if IS_DEMO else "false"))
LOG_LEVEL = str(
    _read_env("LOG_LEVEL", "DEBUG" if DEBUG_MODE else "INFO")
).strip().upper()

DEFAULT_COUNTRY = str(_read_env("DEFAULT_COUNTRY", "México")).strip()
DEFAULT_SECTOR = str(_read_env("DEFAULT_SECTOR", "Tecnología")).strip()
DEFAULT_COMPANY_TYPE = str(_read_env("DEFAULT_COMPANY_TYPE", "PYME")).strip()


# ============================================================
# 6. CONFIGURACIÓN DE MODELOS
# ============================================================

# Se obtienen de las settings centrales
MODEL_NAME = core_settings.MODEL_NAME
FALLBACK_MODEL_NAME = core_settings.FALLBACK_MODEL_NAME
ENABLE_LLM_FALLBACK = core_settings.ENABLE_LLM_FALLBACK
TEMPERATURE = core_settings.TEMPERATURE
MAX_TOKENS = core_settings.MAX_TOKENS


# ============================================================
# 7. CONFIGURACIÓN DE BÚSQUEDA
# ============================================================

# Se obtienen de las settings centrales
SEARCH_DEPTH = core_settings.SEARCH_DEPTH
MAX_RESULTS_PER_QUERY = core_settings.MAX_RESULTS_PER_QUERY


# ============================================================
# 8. CONFIGURACIÓN DE RED / RETRY
# ============================================================

# Se obtienen de las settings centrales
REQUEST_TIMEOUT_SECONDS = core_settings.REQUEST_TIMEOUT_SECONDS
REQUEST_TIMEOUT = core_settings.REQUEST_TIMEOUT_SECONDS # Alias
MAX_RETRIES = core_settings.MAX_RETRIES
INITIAL_BACKOFF_SECONDS = core_settings.INITIAL_BACKOFF_SECONDS
BACKOFF_MULTIPLIER = core_settings.BACKOFF_MULTIPLIER
MAX_BACKOFF_SECONDS = core_settings.MAX_BACKOFF_SECONDS
RETRY_JITTER_SECONDS = core_settings.RETRY_JITTER_SECONDS
THROTTLING_DELAY = core_settings.THROTTLING_DELAY
MIN_RATE_LIMIT_DELAY = core_settings.THROTTLING_DELAY # Alias


# ============================================================
# 9. CONFIGURACIÓN DE CACHÉ
# ============================================================

ENABLE_ANALYSIS_CACHE = _to_bool(_read_env("ENABLE_ANALYSIS_CACHE", "true"))
CACHE_TTL_SECONDS = _to_int(_read_env("CACHE_TTL_SECONDS", 3600), 3600)
CACHE_MAX_ENTRIES = _to_int(_read_env("CACHE_MAX_ENTRIES", 256), 256)


# ============================================================
# 10. CLAVES API
# ============================================================

# Ahora se obtienen de las settings centrales
GROQ_API_KEY = core_settings.GROQ_API_KEY
TAVILY_API_KEY = core_settings.TAVILY_API_KEY


# ============================================================
# 11. CARGA DE YAML
# ============================================================

WEIGHTS_CONFIG: Dict[str, Any] = _load_yaml_file(WEIGHTS_FILE)


# ============================================================
# 12. DIMENSIONES CANÓNICAS DEL SISTEMA
# ============================================================

DEFAULT_COUNTRY_SCORE_DIMENSIONS = [
    "riesgo_politico",
    "estabilidad_economica",
    "riesgo_regulatorio",
    "riesgo_geopolitico",
    "riesgo_comercial",
    "riesgo_operativo",
]

DEFAULT_SECTOR_SCORE_DIMENSIONS = [
    "ajuste_sectorial",
    "oportunidad_sectorial",
]

_DEFAULT_SCORING_WEIGHTS = {
    "riesgo_politico": 0.20,
    "estabilidad_economica": 0.20,
    "riesgo_regulatorio": 0.15,
    "riesgo_comercial": 0.15,
    "riesgo_geopolitico": 0.10,
    "riesgo_operativo": 0.10,
    "ajuste_sectorial": 0.05,
    "oportunidad_sectorial": 0.05,
}

_DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS = {
    "score_riesgo_pais": 0.80,
    "score_riesgo_sectorial": 0.20,
}


def _cargar_weights_yaml() -> Dict[str, Any]:
    """
    Compatibilidad con el cargador desacoplado usado por la suite.

    Devuelve un payload resumido con:
    - `scoring`
    - `country_vs_sector`
    - `app_mode`
    """
    resultado = {
        "scoring": dict(_DEFAULT_SCORING_WEIGHTS),
        "country_vs_sector": dict(_DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS),
        "app_mode": "production",
    }

    if not WEIGHTS_FILE.exists():
        return resultado

    try:
        data = _load_yaml_file(WEIGHTS_FILE)
    except Exception as exc:
        warnings.warn(
            f"No se pudo cargar weights.yaml: {exc}. Se usan defaults y un diccionario válido.",
            RuntimeWarning,
        )
        return resultado

    if not isinstance(data, dict):
        warnings.warn(
            "weights.yaml no contiene un diccionario válido. Se usan defaults.",
            RuntimeWarning,
        )
        return resultado

    scoring = _as_float_dict(data.get("scoring_weights"))
    if scoring:
        merged_scoring = {
            dim: float(scoring.get(dim, peso_default))
            for dim, peso_default in _DEFAULT_SCORING_WEIGHTS.items()
        }
        total = sum(merged_scoring.values())
        if abs(total - 1.0) < 1e-9:
            resultado["scoring"] = merged_scoring
        else:
            warnings.warn(
                "scoring_weights no suma 1.0. Se usan defaults.",
                RuntimeWarning,
            )

    country_vs_sector = _as_float_dict(data.get("country_vs_sector_weights"))
    if country_vs_sector:
        merged_country_vs_sector = {
            "score_riesgo_pais": float(
                country_vs_sector.get(
                    "score_riesgo_pais",
                    _DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS["score_riesgo_pais"],
                )
            ),
            "score_riesgo_sectorial": float(
                country_vs_sector.get(
                    "score_riesgo_sectorial",
                    _DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS["score_riesgo_sectorial"],
                )
            ),
        }
        total = sum(merged_country_vs_sector.values())
        if abs(total - 1.0) < 1e-9:
            resultado["country_vs_sector"] = merged_country_vs_sector
        else:
            warnings.warn(
                "country_vs_sector_weights no suma 1.0. Se usan defaults.",
                RuntimeWarning,
            )

    app_mode = str(data.get("app_mode", "production")).strip().lower()
    if app_mode in {"demo", "production"}:
        resultado["app_mode"] = app_mode
    elif app_mode:
        warnings.warn(
            f"app_mode '{app_mode}' no es válido. Se usa 'production'.",
            RuntimeWarning,
        )

    return resultado


def validar_configuracion_runtime() -> List[str]:
    # Esta validación ahora se delega a la capa compartida
    return core_settings.validar_configuracion_runtime()


def validar_configuracion_api() -> None:
    # Esta validación ahora se delega a la capa compartida
    core_settings.validar_configuracion_api()


def _infer_country_score_dimensions() -> List[str]:
    """
    Reconstruye las dimensiones de riesgo país desde el YAML si existen,
    o usa el conjunto por defecto compatible con scoring.py.
    """
    candidates = [
        WEIGHTS_CONFIG.get("country_score_dimensions"),
        WEIGHTS_CONFIG.get("country_dimensions"),
        WEIGHTS_CONFIG.get("risk_country_dimensions"),
    ]

    for candidate in candidates:
        values = _as_clean_str_list(candidate)
        if values:
            return values

    return DEFAULT_COUNTRY_SCORE_DIMENSIONS.copy()


def _infer_sector_score_dimensions() -> List[str]:
    """
    Reconstruye las dimensiones sectoriales desde el YAML si existen,
    o usa el conjunto por defecto compatible con scoring.py.
    """
    candidates = [
        WEIGHTS_CONFIG.get("sector_score_dimensions"),
        WEIGHTS_CONFIG.get("sector_dimensions"),
        WEIGHTS_CONFIG.get("opportunity_dimensions"),
    ]

    for candidate in candidates:
        values = _as_clean_str_list(candidate)
        if values:
            return values

    return DEFAULT_SECTOR_SCORE_DIMENSIONS.copy()


COUNTRY_SCORE_DIMENSIONS = _infer_country_score_dimensions()
SECTOR_SCORE_DIMENSIONS = _infer_sector_score_dimensions()

# Alias extra de compatibilidad si algún módulo antiguo los usa
SCORE_DIMENSIONS = COUNTRY_SCORE_DIMENSIONS + SECTOR_SCORE_DIMENSIONS
COUNTRY_DIMENSIONS = COUNTRY_SCORE_DIMENSIONS


# ============================================================
# 13. PESOS POR DIMENSIÓN PARA SCORING
# ============================================================


def _infer_scoring_weights() -> Dict[str, float]:
    """
    Construye el diccionario SCORING_WEIGHTS compatible con scoring.py.

    Se intenta leer desde varias claves posibles del YAML.
    Si no hay configuración usable, se aplican pesos uniformes.
    """
    possible_sources = [
        WEIGHTS_CONFIG.get("scoring_weights"),
        WEIGHTS_CONFIG.get("dimension_weights"),
        WEIGHTS_CONFIG.get("weights"),
        WEIGHTS_CONFIG.get("risk_weights"),
    ]

    all_dimensions = COUNTRY_SCORE_DIMENSIONS + SECTOR_SCORE_DIMENSIONS

    for source in possible_sources:
        weights = _as_float_dict(source)
        if weights:
            merged = {}
            for dim in all_dimensions:
                merged[dim] = float(weights.get(dim, 1.0))
            return merged

    return {
        dim: _DEFAULT_SCORING_WEIGHTS.get(dim, 1.0)
        for dim in all_dimensions
    }


SCORING_WEIGHTS = _infer_scoring_weights()

# Alias heredados
WEIGHTS = WEIGHTS_CONFIG
RISK_WEIGHTS = WEIGHTS_CONFIG.get("risk_weights", {})
OPPORTUNITY_WEIGHTS = WEIGHTS_CONFIG.get("opportunity_weights", {})
DIMENSION_WEIGHTS = WEIGHTS_CONFIG.get("dimension_weights", {})


# ============================================================
# 14. PESOS PAÍS VS SECTOR
# ============================================================


def _infer_country_vs_sector_weights() -> Dict[str, float]:
    """
    Construye los pesos de combinación final entre riesgo país y riesgo sectorial.

    scoring.py espera exactamente:
    - score_riesgo_pais
    - score_riesgo_sectorial
    """
    candidates = [
        WEIGHTS_CONFIG.get("country_vs_sector_weights"),
        WEIGHTS_CONFIG.get("aggregate_weights"),
        WEIGHTS_CONFIG.get("final_weights"),
    ]

    for candidate in candidates:
        weights = _as_float_dict(candidate)
        if weights:
            pais = float(weights.get("score_riesgo_pais", 0.6))
            sector = float(weights.get("score_riesgo_sectorial", 0.4))

            normalized = _normalize_weights(
                {
                    "score_riesgo_pais": pais,
                    "score_riesgo_sectorial": sector,
                }
            )

            if (
                "score_riesgo_pais" in normalized
                and "score_riesgo_sectorial" in normalized
            ):
                return normalized

    return dict(_DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS)


COUNTRY_VS_SECTOR_WEIGHTS = _infer_country_vs_sector_weights()


# ============================================================
# 15. VALIDACIONES FINALES
# ============================================================

# Las validaciones generales se realizan en core_settings.py
# Aquí solo las validaciones específicas de este proyecto
if not COUNTRY_SCORE_DIMENSIONS:
    raise RuntimeError("COUNTRY_SCORE_DIMENSIONS no puede quedar vacío.")

if not SECTOR_SCORE_DIMENSIONS:
    raise RuntimeError("SECTOR_SCORE_DIMENSIONS no puede quedar vacío.")


# ============================================================
# 16. EXPORTS
# ============================================================

__all__ = [
    "APP_TITLE",
    "APP_MODE",
    "IS_DEMO",
    "IS_PRODUCTION",
    "BASE_DIR",
    "CONFIG_DIR",
    "DATA_DIR",
    "APP_STORAGE_DIR",
    "ENV_FILE",
    "WEIGHTS_FILE",
    "HISTORY_BASE_DIR",
    "HISTORY_DB_PATH",
    "LOGS_DIR",
    "CACHE_BASE_DIR",
    "DEBUG_MODE",
    "LOG_LEVEL",
    "DEFAULT_COUNTRY",
    "DEFAULT_SECTOR",
    "DEFAULT_COMPANY_TYPE",
    "MODEL_NAME",
    "FALLBACK_MODEL_NAME",
    "ENABLE_LLM_FALLBACK",
    "TEMPERATURE",
    "MAX_TOKENS",
    "SEARCH_DEPTH",
    "MAX_RESULTS_PER_QUERY",
    "REQUEST_TIMEOUT_SECONDS",
    "REQUEST_TIMEOUT",
    "MAX_RETRIES",
    "INITIAL_BACKOFF_SECONDS",
    "BACKOFF_MULTIPLIER",
    "MAX_BACKOFF_SECONDS",
    "RETRY_JITTER_SECONDS",
    "ENABLE_ANALYSIS_CACHE",
    "CACHE_TTL_SECONDS",
    "CACHE_MAX_ENTRIES",
    "GROQ_API_KEY",
    "TAVILY_API_KEY",
    "WEIGHTS_CONFIG",
    "WEIGHTS",
    "RISK_WEIGHTS",
    "OPPORTUNITY_WEIGHTS",
    "DIMENSION_WEIGHTS",
    "SCORING_WEIGHTS",
    "COUNTRY_SCORE_DIMENSIONS",
    "SECTOR_SCORE_DIMENSIONS",
    "SCORE_DIMENSIONS",
    "COUNTRY_DIMENSIONS",
    "COUNTRY_VS_SECTOR_WEIGHTS",
    "THROTTLING_DELAY",
    "MIN_RATE_LIMIT_DELAY",
    # "validar_configuracion_runtime", # Ya no se exporta directamente
    # "validar_configuracion_api", # Ya no se exporta directamente
    "_DEFAULT_SCORING_WEIGHTS",
    "_DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS",
    "_cargar_weights_yaml",
]
