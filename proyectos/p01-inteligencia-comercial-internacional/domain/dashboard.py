"""
domain/dashboard.py
Responsabilidad: Transformar el historial de rankings en tablas para el Dashboard.
"""

from __future__ import annotations
import json
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

from domain import history

import pandas as pd

# Dimensiones para las gráficas
DIMENSIONES_DASHBOARD = [
    "riesgo_politico", "estabilidad_economica", "riesgo_regulatorio",
    "riesgo_geopolitico", "riesgo_comercial", "riesgo_operativo",
    "ajuste_sectorial", "oportunidad_sectorial"
]


def load_historical_rankings() -> List[Dict[str, Any]]:
    """Carga todos los runs del historial en formato {manifest, ranking_data}."""
    results = []
    runs = history.list_ranking_runs()
    for run in runs:
        run_id = run["run_id"]
        ranking_path = history.HISTORY_BASE_DIR / run_id / "ranking.json"
        if ranking_path.exists():
            with open(ranking_path, "r", encoding="utf-8") as f:
                ranking_data = json.load(f)
            results.append({"manifest": run, "ranking_data": ranking_data})
    return results


def build_dashboard_rows(history_payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convierte el historial en filas planas para el dashboard."""
    rows = []
    for entry in history_payload:
        manifest = entry.get("manifest", {})
        ranking_data = entry.get("ranking_data", {})

        generated_at = manifest.get("generated_at", "")
        sector = manifest.get("sector", "")
        company_type = manifest.get("company_type", "")
        run_id = manifest.get("run_id", "")

        for item in ranking_data.get("ranking", []):
            row: Dict[str, Any] = {
                "run_id": run_id,
                "generated_at": generated_at,
                "sector": sector,
                "company_type": company_type,
                "position": item.get("position", 0),
                "country": item.get("country", ""),
                "score_total": item.get("score_total", 0.0),
                "sources_count": len(item.get("sources", [])),
                "executive_summary": item.get("executive_summary", ""),
            }
            for dim, val in item.get("dimension_scores", {}).items():
                row[f"score_{dim}"] = val
            rows.append(row)
    return rows


def compute_dashboard_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {}

    run_ids = {r["run_id"] for r in rows}
    sectors = [r["sector"] for r in rows]

    country_scores: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        country_scores[r["country"]].append(r["score_total"])

    best_country = max(
        country_scores,
        key=lambda c: sum(country_scores[c]) / len(country_scores[c]),
    )

    return {
        "total_runs": len(run_ids),
        "total_country_records": len(rows),
        "unique_countries": len(country_scores),
        "most_used_sector": Counter(sectors).most_common(1)[0][0],
        "best_country_avg": best_country,
    }


def filter_dashboard_rows(
    rows: List[Dict[str, Any]],
    country: Optional[str] = None,
    sector: Optional[str] = None,
    company_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    result = rows
    if country and country != "Todos":
        result = [r for r in result if r["country"] == country]
    if sector and sector != "Todos":
        result = [r for r in result if r["sector"] == sector]
    if company_type and company_type != "Todos":
        result = [r for r in result if r["company_type"] == company_type]
    return result


def get_filter_options(rows: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    countries = sorted({r["country"] for r in rows})
    sectors = sorted({r["sector"] for r in rows})
    company_types = sorted({r["company_type"] for r in rows})
    return {
        "countries": ["Todos"] + countries,
        "sectors": ["Todos"] + sectors,
        "company_types": ["Todos"] + company_types,
    }


def get_country_timeseries(
    rows: List[Dict[str, Any]], country: str
) -> List[Dict[str, Any]]:
    filtered = [r for r in rows if r["country"] == country]
    return sorted(filtered, key=lambda r: r["generated_at"])

def compute_ranking_medio_por_pais(rows: list) -> list:
    if not rows: return []
    df = pd.DataFrame(rows)
    df['rank'] = df.groupby('generated_at')['score_total'].rank(ascending=False)
    res = df.groupby('country')['rank'].mean().sort_values().reset_index()
    res.columns = ['País', 'Ranking Medio']
    return res.to_dict('records')

def compute_dispersion_scores(rows: list) -> list:
    if not rows: return []
    df = pd.DataFrame(rows)
    vol = df.groupby('country')['score_total'].std().fillna(0).reset_index()
    vol.columns = ['País', 'Volatilidad (Std)']
    return vol.to_dict('records')
