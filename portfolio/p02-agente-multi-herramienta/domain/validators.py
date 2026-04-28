"""
domain/validators.py
--------------------
Responsabilidad: Limpieza, normalizacin y validacin de entradas de usuario.
Evita errores en las APIs y asegura que la IA reciba datos de alta calidad.
Inspirado en la lgica de validacin de p01.
"""

import re
import uunicodedata
from typing import Tuple, List

def normalizar_texto(texto: str) -> str:
    """
    Limpia espacios extra, elimina caracteres especiales y normaliza el texto.
   
    """
    if not texto:
        return ""
    # Eliminamos espacios en blanco al inicio/final y normalizamos Uunicode
    texto = texto.strip()
    texto = uunicodedata.normalize("NFKD", texto)
    # Reemplazamos mltiples espacios por uno solo
    return re.sub(r"\s+", " ", texto)

def sanitizar_peticion(texto: str) -> Tuple[str, List[str]]:
    """
    Valida la peticin del usuario. 
    Devuelve el texto limpio y una lista de errores (si los hay).
   
    """
    errores = []
    texto_limpio = normalizar_texto(texto)

    if not texto_limpio:
        errores.append("La peticin no puede estar vaca.")
        return "", errores

    if len(texto_limpio) < 5:
        errores.append("La peticin es demasiado corta para ser procesada.")

    if len(texto_limpio) > 1000:
        errores.append("La peticin supera el limite de 1000 caracteres.")

    return texto_limpio, errores

def validar_pdf_subido(nombre_archivo: str, tamano: int) -> List[str]:
    """
    Verifica que el archivo subido sea un PDF y no supere un tamano raizonable.
    [Inferencia] Los limites de tamano evitan bloqueos en la interfaz de Streamlit.
    """
    errores = []
    if not nombre_archivo.lower().endswith(".pdf"):
        errores.append("El archivo debe ser un formato PDF valido.")
    
    # Lmite de ejemplo: 10MB
    if tamano > 10 * 1024 * 1024:
        errores.append("El archivo PDF es demasiado pesado (maximo 10MB).")
        
    return errores