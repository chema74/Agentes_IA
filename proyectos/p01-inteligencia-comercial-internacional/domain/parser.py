"""
parser.py

Responsabilidad:
- limpiar la salida textual del LLM
- extraer el JSON util
- validarlo contra el contrato narrativo canonico
"""

from __future__ import annotations

import json

from domain.schemas import AnalisisNarrativoLLM


def clean_json(raw: str) -> dict:
    """
    Limpia y valida la respuesta del modelo.
    """

    # ---------------------------------------------------------------
    # 1. Validacion basica de entrada
    # ---------------------------------------------------------------
    if raw is None:
        raise ValueError("Respuesta del modelo vacia.")

    if not isinstance(raw, str):
        raise ValueError("La respuesta del modelo no es texto.")

    raw = raw.strip()

    if not raw:
        raise ValueError("La respuesta del modelo esta vacia.")

    # ---------------------------------------------------------------
    # 2. Eliminar posibles bloques Markdown
    # ---------------------------------------------------------------
    if "```" in raw:
        for part in raw.split("```"):
            fragment = part.strip()

            if fragment.lower().startswith("json"):
                fragment = fragment[4:].strip()

            if fragment.startswith("{"):
                raw = fragment
                break

    # ---------------------------------------------------------------
    # 3. Extraer el bloque JSON principal
    # ---------------------------------------------------------------
    start = raw.find("{")
    end = raw.rfind("}")

    if start != -1 and end != -1 and end > start:
        raw = raw[start : end + 1]

    # ---------------------------------------------------------------
    # 4. Parsear JSON bruto
    # ---------------------------------------------------------------
    data = json.loads(raw)

    # ---------------------------------------------------------------
    # 5. Validar contra el contrato narrativo canonico
    # ---------------------------------------------------------------
    validated = AnalisisNarrativoLLM.model_validate(data)

    # ---------------------------------------------------------------
    # 6. Devolver un dict canonico consumible por la app
    # ---------------------------------------------------------------
    return validated.model_dump()
