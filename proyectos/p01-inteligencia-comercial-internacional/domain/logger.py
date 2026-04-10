from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "app_events.jsonl"


def ensure_logs_dir() -> Path:
    """
    Garantiza que exista el directorio de logs.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def log_event(
    event_type: str,
    payload: Dict[str, Any] | None = None,
) -> Path:
    """
    Registra un evento en formato JSON Lines.

    Cada línea del archivo representa un evento independiente.
    """
    ensure_logs_dir()

    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": event_type,
        "payload": payload or {},
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return LOG_FILE


def read_recent_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Lee los eventos más recientes del archivo JSONL.
    """
    ensure_logs_dir()

    if not LOG_FILE.exists():
        return []

    events: List[Dict[str, Any]] = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue

        try:
            events.append(json.loads(line))
        except Exception:
            continue

    return list(reversed(events))


def clear_logs() -> int:
    """
    Borra el archivo de logs y devuelve cuántas líneas tenía.
    """
    ensure_logs_dir()

    if not LOG_FILE.exists():
        return 0

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        count = len(f.readlines())

    LOG_FILE.unlink(missing_ok=True)
    return count


def get_log_stats() -> Dict[str, Any]:
    """
    Devuelve estadísticas simples del sistema de logs.
    """
    ensure_logs_dir()

    total_events = 0
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            total_events = sum(1 for _ in f)

    return {
        "logs_dir": str(LOGS_DIR),
        "log_file": str(LOG_FILE),
        "total_events": total_events,
    }