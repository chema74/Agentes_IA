"""
comparativa.py

Responsabilidad:
comparar dos ejecuciones históricas de ranking de forma inteligente.

Fase 14:
- carga dos runs del histórico por su run_id
- compara scores totales por país
- detecta subidas y bajadas de score
- compara dimensiones entre runs
- devuelve un informe estructurado de cambios

Este módulo no modifica ningún archivo existente.
Se integra como sección nueva en streamlit_app.py.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from domain.history import load_ranking_run, list_ranking_runs
from domain.logger import log_event


# -------------------------------------------------------------------
# 1. CONSTANTES
# -------------------------------------------------------------------

# Umbral mínimo de cambio para considerar una variación significativa
UMBRAL_CAMBIO_SIGNIFICATIVO = 0.5


# -------------------------------------------------------------------
# 2. CARGA DE DATOS DE UN RUN
# -------------------------------------------------------------------

def cargar_scores_de_run(run_id: str) -> Dict[str, Any]:
    """
    Carga el manifest y el JSON de ranking de un run concreto.

    Devuelve un diccionario con:
    - run_id
    - generated_at
    - sector
    - company_type
    - paises: dict {nombre_pais: {score_total, dimension_scores}}
    """
    from pathlib import Path
    import json

    manifest = load_ranking_run(run_id)
    artifacts = manifest.get("artifacts", {})
    json_path = artifacts.get("json")

    if not json_path or not Path(json_path).exists():
        raise FileNotFoundError(
            f"No se encontró el archivo JSON del ranking para run_id={run_id}"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        ranking_data = json.load(f)

    paises: Dict[str, Dict[str, Any]] = {}

    for item in ranking_data.get("ranking", []):
        nombre = item.get("country", "")
        if not nombre:
            continue

        paises[nombre] = {
            "score_total": float(item.get("score_total", 0)),
            "position": int(item.get("position", 0)),
            "dimension_scores": {
                k: float(v)
                for k, v in item.get("dimension_scores", {}).items()
            },
            "executive_summary": item.get("executive_summary", ""),
        }

    return {
        "run_id": run_id,
        "generated_at": manifest.get("generated_at", ""),
        "sector": manifest.get("sector", ""),
        "company_type": manifest.get("company_type", ""),
        "paises": paises,
    }


# -------------------------------------------------------------------
# 3. COMPARACIÓN ENTRE DOS RUNS
# -------------------------------------------------------------------

def comparar_runs(
    run_id_a: str,
    run_id_b: str,
) -> Dict[str, Any]:
    """
    Compara dos ejecuciones históricas de ranking.

    Devuelve un informe estructurado con:
    - metadatos de ambos runs
    - países comunes analizados en los dos runs
    - cambios de score total por país (subida / bajada / sin cambio)
    - cambios por dimensión para cada país común
    - resumen ejecutivo de los cambios más significativos
    """

    log_event(
        "comparativa_runs_started",
        {
            "run_id_a": run_id_a,
            "run_id_b": run_id_b,
        },
    )

    # ---------------------------------------------------------------
    # 3.1. Cargar los dos runs
    # ---------------------------------------------------------------
    datos_a = cargar_scores_de_run(run_id_a)
    datos_b = cargar_scores_de_run(run_id_b)

    paises_a = datos_a["paises"]
    paises_b = datos_b["paises"]

    # ---------------------------------------------------------------
    # 3.2. Países comunes y exclusivos
    # ---------------------------------------------------------------
    nombres_a = set(paises_a.keys())
    nombres_b = set(paises_b.keys())

    paises_comunes = sorted(nombres_a & nombres_b)
    solo_en_a = sorted(nombres_a - nombres_b)
    solo_en_b = sorted(nombres_b - nombres_a)

    # ---------------------------------------------------------------
    # 3.3. Comparar score total por país común
    # ---------------------------------------------------------------
    cambios_score_total: List[Dict[str, Any]] = []

    for pais in paises_comunes:
        score_a = paises_a[pais]["score_total"]
        score_b = paises_b[pais]["score_total"]
        diferencia = round(score_b - score_a, 2)
        abs_diferencia = abs(diferencia)

        if diferencia > UMBRAL_CAMBIO_SIGNIFICATIVO:
            tendencia = "sube"
        elif diferencia < -UMBRAL_CAMBIO_SIGNIFICATIVO:
            tendencia = "baja"
        else:
            tendencia = "estable"

        cambios_score_total.append(
            {
                "pais": pais,
                "score_run_a": score_a,
                "score_run_b": score_b,
                "diferencia": diferencia,
                "abs_diferencia": abs_diferencia,
                "tendencia": tendencia,
                "significativo": abs_diferencia >= UMBRAL_CAMBIO_SIGNIFICATIVO,
            }
        )

    # Ordenar por cambio más significativo primero
    cambios_score_total.sort(key=lambda x: x["abs_diferencia"], reverse=True)

    # ---------------------------------------------------------------
    # 3.4. Comparar dimensiones por país común
    # ---------------------------------------------------------------
    cambios_por_dimension: Dict[str, List[Dict[str, Any]]] = {}

    for pais in paises_comunes:
        dims_a = paises_a[pais].get("dimension_scores", {})
        dims_b = paises_b[pais].get("dimension_scores", {})

        dimensiones_comunes = set(dims_a.keys()) & set(dims_b.keys())
        cambios_dims: List[Dict[str, Any]] = []

        for dim in sorted(dimensiones_comunes):
            val_a = dims_a[dim]
            val_b = dims_b[dim]
            diferencia_dim = round(val_b - val_a, 2)

            if diferencia_dim > UMBRAL_CAMBIO_SIGNIFICATIVO:
                tendencia_dim = "sube"
            elif diferencia_dim < -UMBRAL_CAMBIO_SIGNIFICATIVO:
                tendencia_dim = "baja"
            else:
                tendencia_dim = "estable"

            cambios_dims.append(
                {
                    "dimension": dim,
                    "valor_run_a": val_a,
                    "valor_run_b": val_b,
                    "diferencia": diferencia_dim,
                    "tendencia": tendencia_dim,
                    "significativo": abs(diferencia_dim) >= UMBRAL_CAMBIO_SIGNIFICATIVO,
                }
            )

        cambios_dims.sort(key=lambda x: abs(x["diferencia"]), reverse=True)
        cambios_por_dimension[pais] = cambios_dims

    # ---------------------------------------------------------------
    # 3.5. Resumen de cambios más significativos
    # ---------------------------------------------------------------
    paises_que_suben = [
        c["pais"] for c in cambios_score_total
        if c["tendencia"] == "sube" and c["significativo"]
    ]
    paises_que_bajan = [
        c["pais"] for c in cambios_score_total
        if c["tendencia"] == "baja" and c["significativo"]
    ]
    paises_estables = [
        c["pais"] for c in cambios_score_total
        if c["tendencia"] == "estable"
    ]

    log_event(
        "comparativa_runs_completed",
        {
            "run_id_a": run_id_a,
            "run_id_b": run_id_b,
            "paises_comunes": len(paises_comunes),
            "paises_que_suben": len(paises_que_suben),
            "paises_que_bajan": len(paises_que_bajan),
        },
    )

    return {
        "run_a": {
            "run_id": datos_a["run_id"],
            "generated_at": datos_a["generated_at"],
            "sector": datos_a["sector"],
            "company_type": datos_a["company_type"],
        },
        "run_b": {
            "run_id": datos_b["run_id"],
            "generated_at": datos_b["generated_at"],
            "sector": datos_b["sector"],
            "company_type": datos_b["company_type"],
        },
        "paises_comunes": paises_comunes,
        "solo_en_run_a": solo_en_a,
        "solo_en_run_b": solo_en_b,
        "cambios_score_total": cambios_score_total,
        "cambios_por_dimension": cambios_por_dimension,
        "resumen": {
            "total_paises_comunes": len(paises_comunes),
            "paises_que_suben": paises_que_suben,
            "paises_que_bajan": paises_que_bajan,
            "paises_estables": paises_estables,
        },
    }


# -------------------------------------------------------------------
# 4. UTILIDADES DE PRESENTACIÓN
# -------------------------------------------------------------------

def etiqueta_tendencia(tendencia: str) -> str:
    """
    Devuelve una etiqueta visual para la tendencia.
    """
    return {
        "sube": "⬆ Sube",
        "baja": "⬇ Baja",
        "estable": "➡ Estable",
    }.get(tendencia, "—")


def etiqueta_dimension(dimension: str) -> str:
    """
    Convierte clave técnica de dimensión a etiqueta legible.
    """
    etiquetas = {
        "riesgo_politico": "Riesgo político",
        "estabilidad_economica": "Estabilidad económica",
        "riesgo_regulatorio": "Riesgo regulatorio",
        "riesgo_geopolitico": "Riesgo geopolítico",
        "riesgo_comercial": "Riesgo comercial",
        "riesgo_operativo": "Riesgo operativo",
        "ajuste_sectorial": "Ajuste sectorial",
        "oportunidad_sectorial": "Oportunidad sectorial",
    }
    return etiquetas.get(dimension, dimension.replace("_", " ").capitalize())


def get_runs_disponibles() -> List[Dict[str, Any]]:
    """
    Devuelve la lista de runs disponibles para comparar.
    Wrapper sobre list_ranking_runs para uso en la UI.
    """
    return list_ranking_runs()