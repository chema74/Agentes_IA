"""
domain/history.py
Responsabilidad: persistencia mínima de runs y rankings.

Regla de esta fase:
- SQLite es el backend principal nuevo.
- JSON legacy se mantiene como artefacto compatible y fallback de lectura.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.settings import (
    APP_MODE,
    HISTORY_BASE_DIR as SETTINGS_HISTORY_BASE_DIR,
    HISTORY_DB_PATH as SETTINGS_HISTORY_DB_PATH,
)
from domain.schemas import RankingResult

HISTORY_BASE_DIR = pathlib.Path(SETTINGS_HISTORY_BASE_DIR)
HISTORY_DB_PATH = pathlib.Path(SETTINGS_HISTORY_DB_PATH)


def _ensure_history_dir() -> pathlib.Path:
    HISTORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_BASE_DIR


def _ensure_db_parent_dir() -> pathlib.Path:
    HISTORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return HISTORY_DB_PATH.parent


def _get_connection() -> sqlite3.Connection:
    _ensure_db_parent_dir()
    conn = sqlite3.connect(HISTORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _initialize_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            generated_at TEXT NOT NULL,
            mode TEXT NOT NULL,
            sector TEXT,
            company_type TEXT,
            countries_requested_json TEXT,
            total_countries INTEGER,
            source_format TEXT NOT NULL DEFAULT 'sqlite',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            country TEXT NOT NULL,
            score_total REAL,
            summary_json TEXT,
            raw_result_json TEXT,
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        )
        """
    )
    conn.commit()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def build_run_manifest(
    ranking_result: RankingResult,
    artifacts: Dict[str, str],
    status: str = "success",
) -> Dict[str, Any]:
    return {
        "run_id": ranking_result.metadata.run_id,
        "generated_at": ranking_result.metadata.generated_at,
        "mode": APP_MODE,
        "sector": ranking_result.metadata.sector,
        "company_type": ranking_result.metadata.company_type,
        "countries_requested": ranking_result.metadata.countries_requested,
        "total_countries": ranking_result.metadata.total_countries,
        "version": ranking_result.metadata.version,
        "status": status,
        "source_format": "sqlite",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "artifacts": artifacts,
    }


def _save_run_to_sqlite(
    ranking_result: RankingResult,
    status: str,
) -> None:
    metadata = ranking_result.metadata

    with _get_connection() as conn:
        _initialize_db(conn)
        conn.execute("DELETE FROM rankings WHERE run_id = ?", (metadata.run_id,))
        conn.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_id,
                generated_at,
                mode,
                sector,
                company_type,
                countries_requested_json,
                total_countries,
                source_format,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata.run_id,
                metadata.generated_at,
                APP_MODE,
                metadata.sector,
                metadata.company_type,
                _json_dumps(metadata.countries_requested),
                metadata.total_countries,
                "sqlite",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        for item in ranking_result.ranking:
            conn.execute(
                """
                INSERT INTO rankings (
                    run_id,
                    position,
                    country,
                    score_total,
                    summary_json,
                    raw_result_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata.run_id,
                    item.position,
                    item.country,
                    item.score_total,
                    _json_dumps(item.executive_summary),
                    _json_dumps(item.raw_result),
                ),
            )

        conn.commit()


def _save_run_to_legacy_json(
    ranking_result: RankingResult,
    artifact_paths: Dict[str, pathlib.Path],
    status: str,
) -> pathlib.Path:
    _ensure_history_dir()
    run_dir = HISTORY_BASE_DIR / ranking_result.metadata.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {key: str(path) for key, path in artifact_paths.items()}
    manifest = build_run_manifest(ranking_result, artifacts, status)

    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    with open(run_dir / "ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking_result.model_dump(), f, ensure_ascii=False, indent=2)

    return run_dir


def save_ranking_run(
    ranking_result: RankingResult,
    artifact_paths: Dict[str, pathlib.Path],
    status: str = "success",
) -> pathlib.Path:
    """
    Paso 1: guardar en SQLite como backend principal.
    Paso 2: seguir materializando JSON legacy para compatibilidad mínima.
    """
    _save_run_to_sqlite(ranking_result=ranking_result, status=status)
    return _save_run_to_legacy_json(
        ranking_result=ranking_result,
        artifact_paths=artifact_paths,
        status=status,
    )


def _build_manifest_from_sqlite_row(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "run_id": row["run_id"],
        "generated_at": row["generated_at"],
        "mode": row["mode"],
        "sector": row["sector"] or "",
        "company_type": row["company_type"] or "",
        "countries_requested": _json_loads(row["countries_requested_json"], []),
        "total_countries": row["total_countries"] or 0,
        "source_format": row["source_format"] or "sqlite",
        "created_at": row["created_at"],
        "status": "success",
        "artifacts": {
            "manifest": str(HISTORY_BASE_DIR / row["run_id"] / "manifest.json"),
            "json": str(HISTORY_BASE_DIR / row["run_id"] / "ranking.json"),
        },
    }


def _list_ranking_runs_from_sqlite() -> List[Dict[str, Any]]:
    if not HISTORY_DB_PATH.exists():
        return []

    with _get_connection() as conn:
        _initialize_db(conn)
        rows = conn.execute(
            """
            SELECT run_id, generated_at, mode, sector, company_type,
                   countries_requested_json, total_countries,
                   source_format, created_at
            FROM runs
            ORDER BY created_at ASC, run_id ASC
            """
        ).fetchall()

    return [_build_manifest_from_sqlite_row(row) for row in rows]


def _list_ranking_runs_from_json() -> List[Dict[str, Any]]:
    if not HISTORY_BASE_DIR.exists():
        return []

    runs = []
    for d in sorted(HISTORY_BASE_DIR.iterdir()):
        manifest_path = d / "manifest.json"
        if d.is_dir() and manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                runs.append(json.load(f))
    return runs


def list_ranking_runs() -> List[Dict[str, Any]]:
    runs = _list_ranking_runs_from_sqlite()
    if runs:
        return runs
    return _list_ranking_runs_from_json()


def _load_ranking_run_from_sqlite(run_id: str) -> Optional[Dict[str, Any]]:
    if not HISTORY_DB_PATH.exists():
        return None

    with _get_connection() as conn:
        _initialize_db(conn)
        row = conn.execute(
            """
            SELECT run_id, generated_at, mode, sector, company_type,
                   countries_requested_json, total_countries,
                   source_format, created_at
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()

    if row is None:
        return None
    return _build_manifest_from_sqlite_row(row)


def load_ranking_run(run_id: str) -> Optional[Dict[str, Any]]:
    sqlite_manifest = _load_ranking_run_from_sqlite(run_id)
    if sqlite_manifest is not None:
        return sqlite_manifest

    manifest_path = HISTORY_BASE_DIR / run_id / "manifest.json"
    if not manifest_path.exists():
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_ranking_payload_from_sqlite(run_id: str) -> Optional[Dict[str, Any]]:
    manifest = _load_ranking_run_from_sqlite(run_id)
    if manifest is None:
        return None

    with _get_connection() as conn:
        _initialize_db(conn)
        rows = conn.execute(
            """
            SELECT position, country, score_total, summary_json, raw_result_json
            FROM rankings
            WHERE run_id = ?
            ORDER BY position ASC, id ASC
            """,
            (run_id,),
        ).fetchall()

    ranking_items = []
    for row in rows:
        raw_result = _json_loads(row["raw_result_json"], {})
        if not isinstance(raw_result, dict):
            raw_result = {}

        fuentes_raw = raw_result.get("fuentes", [])
        sources = []
        if isinstance(fuentes_raw, list):
            for source in fuentes_raw:
                if not isinstance(source, dict):
                    continue
                sources.append(
                    {
                        "category": str(source.get("categoria", "")),
                        "title": str(source.get("titulo", "")),
                        "url": str(source.get("url", "")),
                        "summary": str(source.get("resumen", "")),
                    }
                )

        executive_summary = _json_loads(row["summary_json"], "")
        if not isinstance(executive_summary, str):
            executive_summary = str(executive_summary)

        ranking_items.append(
            {
                "position": row["position"],
                "country": row["country"],
                "score_total": float(row["score_total"] or 0.0),
                "dimension_scores": raw_result.get("scores", {}),
                "executive_summary": executive_summary,
                "sources": sources,
                "raw_result": raw_result,
            }
        )

    ranking_data = {
        "metadata": {
            "run_id": manifest["run_id"],
            "generated_at": manifest["generated_at"],
            "sector": manifest["sector"],
            "company_type": manifest["company_type"],
            "countries_requested": manifest.get("countries_requested", []),
            "total_countries": manifest.get("total_countries", 0),
            "version": manifest.get("source_format", "sqlite"),
        },
        "ranking": ranking_items,
    }

    return {"manifest": manifest, "ranking_data": ranking_data}


def load_ranking_payload(run_id: str) -> Optional[Dict[str, Any]]:
    sqlite_payload = _build_ranking_payload_from_sqlite(run_id)
    if sqlite_payload is not None:
        return sqlite_payload

    manifest = load_ranking_run(run_id)
    if manifest is None:
        return None

    ranking_path = HISTORY_BASE_DIR / run_id / "ranking.json"
    if not ranking_path.exists():
        return None

    with open(ranking_path, "r", encoding="utf-8") as f:
        ranking_data = json.load(f)

    return {"manifest": manifest, "ranking_data": ranking_data}
