"""
domain/validators.py
--------------------
Responsabilidad: Limpieza, normalización y validación de entradas de usuario.
Evita errores en las APIs y asegura que la IA reciba datos de alta calidad.
Inspirado en la lógica de validación de p01.
"""

import re
import unicodedata
from typing import Tuple, List

def normalizar_texto(texto: str) -> str:
    """
    Limpia espacios extra, elimina caracteres especiales y normaliza el texto.
   
    """
    if not texto:
        return ""
    # Eliminamos espacios en blanco al inicio/final y normalizamos Unicode
    texto = texto.strip()
    texto = unicodedata.normalize("NFKD", texto)
    # Reemplazamos múltiples espacios por uno solo
    return re.sub(r"\s+", " ", texto)

def sanitizar_peticion(texto: str) -> Tuple[str, List[str]]:
    """
    Valida la petición del usuario. 
    Devuelve el texto limpio y una lista de errores (si los hay).
   
    """
    errores = []
    texto_limpio = normalizar_texto(texto)

    if not texto_limpio:
        errores.append("La petición no puede estar vacía.")
        return "", errores

    if len(texto_limpio) < 5:
        errores.append("La petición es demasiado corta para ser procesada.")

    if len(texto_limpio) > 1000:
        errores.append("La petición supera el límite de 1000 caracteres.")

    return texto_limpio, errores

def validar_pdf_subido(nombre_archivo: str, tamaño: int) -> List[str]:
    """
    Verifica que el archivo subido sea un PDF y no supere un tamaño razonable.
    [Inferencia] Los límites de tamaño evitan bloqueos en la interfaz de Streamlit.
    """
    errores = []
    if not nombre_archivo.lower().endswith(".pdf"):
        errores.append("El archivo debe ser un formato PDF válido.")
    
    # Límite de ejemplo: 10MB
    if tamaño > 10 * 1024 * 1024:
        errores.append("El archivo PDF es demasiado pesado (máximo 10MB).")
        
    return errores