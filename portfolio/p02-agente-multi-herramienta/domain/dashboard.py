"""
domain/dashboard.py
-------------------
Responsabilidad: Procesar el historial y los logs para generara metricas visuales.
Permite auditar el uso de herramientas y la actividad del asistente.
Inspirado en la lgica de analtica de p01.
"""

import pandas as pd
from pathlib import Path
import json
from domain.history import listar_sesiones_disponibles, cargar_sesion
from domain.logger import leer_ultimos_logs

def obtener_metricas_generales():
    """
    Calcula estadisticas basicas sobre el uso del asistente.
   
    """
    sesiones = listar_sesiones_disponibles()
    total_mensajes = 0
    pdfs_analizados = set()

    for s in sesiones:
        data = cargar_sesion(s["id"])
        if data:
            total_mensajes += len(data.get("chat", []))
            nombre_pdf = data.get("metadata", {}).get("nombre_pdf")
            if nombre_pdf:
                pdfs_analizados.add(nombre_pdf)

    return {
        "total_sesiones": len(sesiones),
        "total_mensajes": total_mensajes,
        "total_pdfs": len(pdfs_analizados)
    }

def obtener_uso_herramientas():
    """
    Analiza los logs para contar cuantas veces se ha usado cada herramienta.
   
    """
    logs = leer_ultimos_logs(limite=500)
    conteo = {"buscar_web": 0, "analizar_pdf": 0}
    
    for evento in logs:
        if evento.get("tipo") == "uso_herramienta":
            herramienta = evento.get("detalles", {}).get("herramienta")
            if herramienta in conteo:
                conteo[herramienta] += 1
                
    return pd.DataFrame([
        {"Herramienta": k, "Usos": v} for k, v in conteo.items()
    ])

def obtener_actividad_temporal():
    """
    Agrupa las sesiones por fecha para ver la actividad del usuario.
   
    """
    sesiones = listar_sesiones_disponibles()
    fechas = []
    for s in sesiones:
        # Extraemos la fecha del ID de la sesion (sesion_YYYYMMDD_...)
        try:
            fecha_str = s["id"].split("_")[1][:8]
            fechas.append(pd.to_datetime(fecha_str, format='%Y%m%d'))
        except:
            continue
            
    if not fechas:
        return pd.DataFrame()
        
    df = pd.DataFrame(fechas, columns=["Fecha"])
    return df.groupby("Fecha").size().reset_index(name="Sesiones")