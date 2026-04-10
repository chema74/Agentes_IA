from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any, Dict

from config.settings import CACHE_BASE_DIR as SETTINGS_CACHE_BASE_DIR

CACHE_BASE_DIR = Path(SETTINGS_CACHE_BASE_DIR)


def ensure_cache_dir() -> Path:
    """
    Garantiza que exista el directorio base de caché.
    """
    CACHE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_BASE_DIR


def _normalize_text(text: str) -> str:
    """
    Normaliza texto para construir claves estables.
    """
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text


def build_cache_key(
    pais: str,
    sector: str,
    tipo_empresa: str,
) -> str:
    """
    Construye una clave de caché estable para un análisis de país.
    """
    raw_key = "||".join(
        [
            _normalize_text(pais),
            _normalize_text(sector),
            _normalize_text(tipo_empresa),
        ]
    )
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def get_cache_file_path(
    pais: str,
    sector: str,
    tipo_empresa: str,
) -> Path:
    """
    Devuelve la ruta del archivo de caché para una combinación dada.
    """
    ensure_cache_dir()
    cache_key = build_cache_key(
        pais=pais,
        sector=sector,
        tipo_empresa=tipo_empresa,
    )
    return CACHE_BASE_DIR / f"{cache_key}.json"


def load_country_analysis_from_cache(
    pais: str,
    sector: str,
    tipo_empresa: str,
) -> Dict[str, Any] | None:
    """
    Carga un análisis desde caché si existe.
    """
    try:
        cache_file = get_cache_file_path(
            pais=pais,
            sector=sector,
            tipo_empresa=tipo_empresa,
        )
    except OSError:
        return None

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    return data


def save_country_analysis_to_cache(
    pais: str,
    sector: str,
    tipo_empresa: str,
    data: Dict[str, Any],
) -> Path | None:
    """
    Guarda un análisis de país en caché.
    """
    try:
        cache_file = get_cache_file_path(
            pais=pais,
            sector=sector,
            tipo_empresa=tipo_empresa,
        )
    except OSError:
        return None

    payload = {
        "metadata": {
            "pais": pais,
            "sector": sector,
            "tipo_empresa": tipo_empresa,
            "cache_key": build_cache_key(pais, sector, tipo_empresa),
        },
        "result": data,
    }

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
    except OSError:
        return None

    return cache_file


def clear_country_analysis_cache() -> int:
    """
    Borra todos los archivos de caché y devuelve cuántos se eliminaron.
    """
    try:
        ensure_cache_dir()
    except OSError:
        return 0

    deleted = 0
    for file_path in CACHE_BASE_DIR.glob("*.json"):
        file_path.unlink(missing_ok=True)
        deleted += 1

    return deleted


def get_cache_stats() -> Dict[str, Any]:
    """
    Devuelve estadísticas simples de caché.
    """
    try:
        ensure_cache_dir()
    except OSError:
        return {
            "cache_dir": str(CACHE_BASE_DIR),
            "total_files": 0,
        }
    files = list(CACHE_BASE_DIR.glob("*.json"))

    return {
        "cache_dir": str(CACHE_BASE_DIR),
        "total_files": len(files),
    }
