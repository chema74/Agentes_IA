"""
domain/history.py
-----------------
Responsabilidad: Persistencia física de las sesiones de chat y contextos.
Permite que el asistente 'recuerde' conversaciones pasadas entre reinicios.
Inspirado en la lógica de guardado de ejecuciones de p01.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Definimos la carpeta de historial en la raíz del proyecto
HISTORY_DIR = Path("history")

def asegurar_directorio_historial() -> Path:
    """Garantiza que la carpeta history/ exista."""
    HISTORY_DIR.mkdir(exist_ok=True)
    return HISTORY_DIR

def generar_id_sesion(nombre_pdf: str = "general") -> str:
    """Crea un ID único basado en la fecha y el tema del análisis."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Limpiamos el nombre del archivo para que sea un nombre de carpeta válido
    nombre_limpio = "".join(filter(str.isalnum, nombre_pdf))[:20]
    return f"sesion_{timestamp}_{nombre_limpio}"

def guardar_sesion(id_sesion: str, mensajes: List[Dict[str, Any]], nombre_pdf: str = ""):
    """
    Guarda el historial de mensajes y metadatos en un archivo JSON.
    """
    asegurar_directorio_historial()
    ruta_archivo = HISTORY_DIR / f"{id_sesion}.json"
    
    payload = {
        "metadata": {
            "id": id_sesion,
            "fecha_creacion": datetime.now().isoformat(),
            "nombre_pdf": nombre_pdf,
            "total_mensajes": len(mensajes)
        },
        "chat": mensajes
    }
    
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def cargar_sesion(id_sesion: str) -> Optional[Dict[str, Any]]:
    """Carga una sesión específica desde el disco."""
    ruta_archivo = HISTORY_DIR / f"{id_sesion}.json"
    if not ruta_archivo.exists():
        return None
    
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"🚨 Error al cargar la sesión {id_sesion}: {e}")
        return None

def listar_sesiones_disponibles() -> List[Dict[str, str]]:
    """Devuelve una lista de sesiones guardadas para mostrar en la interfaz."""
    asegurar_directorio_historial()
    sesiones = []
    
    # Buscamos todos los archivos .json en la carpeta history
    for archivo in HISTORY_DIR.glob("*.json"):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                meta = data.get("metadata", {})
                sesiones.append({
                    "id": meta.get("id"),
                    "label": f"📅 {meta.get('fecha_creacion')[:16]} - 📄 {meta.get('nombre_pdf') or 'Sin PDF'}"
                })
        except:
            continue
            
    # Ordenamos por las más recientes primero
    return sorted(sesiones, key=lambda x: x["id"], reverse=True)