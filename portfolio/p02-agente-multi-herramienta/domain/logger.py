"""
domain/logger.py
----------------
Sistema de registro de eventos estructurado (Observabilidad).
Inspirado en la arquitectura de traizabilidad de p01.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Definimos la ruta del archivo de log dentro del proyecto
LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "agente_ejecutivo.jsonl"

def asegurar_directorio_logs():
    """Garantiza que la carpeta de logs exista."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def registrar_evento(tipo_evento: str, datos: Dict[str, Any] | None = None):
    """
    Guarda un evento en el archivo .jsonl. 
    Cada lnea es un objeto JSON independiente, lo que facilita su lectura posterior.
    """
    asegurar_directorio_logs()

    # Estructura estndar del log
    evento = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tipo": tipo_evento,
        "detalles": datos or {}
    }

    # 'a' (append) para anadir al final del archivo sin borrar lo anterior
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")

def leer_ultimos_logs(limite: int = 50) -> List[Dict[str, Any]]:
    """Lee los ltimos eventos para mostrarlos en la interfaz si fuera necesario."""
    if not LOG_FILE.exists():
        return []

    eventos = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lineas = f.readlines()
        for linea in lineas[-limite:]:
            try:
                eventos.append(json.loads(linea.strip()))
            except:
                continue
    return list(reversed(eventos))

def limpiar_logs():
    """Borra el historial de logs."""
    if LOG_FILE.exists():
        LOG_FILE.unlink()