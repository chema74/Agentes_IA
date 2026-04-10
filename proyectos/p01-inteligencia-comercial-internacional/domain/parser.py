"""
parser.py

Responsabilidad:
- limpiar la salida textual del LLM
- extraer el JSON útil
- validarlo contra el esquema esperado

En esta fase validamos la salida narrativa del modelo,
NO el resultado final con scores.
"""

import json
from domain.schemas import AnalisisNarrativoLLM


def clean_json(raw: str) -> dict:
    """
    Limpia y valida la respuesta del modelo.
    """

    # ---------------------------------------------------------------
    # 1. VALIDACIÓN BÁSICA DE ENTRADA
    # ---------------------------------------------------------------
    if raw is None:
        raise ValueError("Respuesta del modelo vacía")

    if not isinstance(raw, str):
        raise ValueError("La respuesta del modelo no es texto")

    raw = raw.strip()

    if not raw:
        raise ValueError("La respuesta del modelo está vacía")

    # ---------------------------------------------------------------
    # 2. ELIMINAR POSIBLES BLOQUES MARKDOWN
    # ---------------------------------------------------------------
    if "```" in raw:
        for part in raw.split("```"):
            fragmento = part.strip()

            if fragmento.lower().startswith("json"):
                fragmento = fragmento[4:].strip()

            if fragmento.startswith("{"):
                raw = fragmento
                break

    # ---------------------------------------------------------------
    # 3. EXTRAER DESDE EL PRIMER { HASTA EL ÚLTIMO }
    # ---------------------------------------------------------------
    start = raw.find("{")
    end = raw.rfind("}")

    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]

    # ---------------------------------------------------------------
    # 4. PARSEAR JSON
    # ---------------------------------------------------------------
    data = json.loads(raw)

    # ---------------------------------------------------------------
    # 5. VALIDACIÓN FUERTE CON PYDANTIC
    # ---------------------------------------------------------------
    validated = AnalisisNarrativoLLM(**data)

    # ---------------------------------------------------------------
    # 6. DEVOLVER COMO DICCIONARIO PYTHON
    # ---------------------------------------------------------------
    return validated.dict()