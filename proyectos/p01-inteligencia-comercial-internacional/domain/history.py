"""
domain/history.py
Responsabilidad: Persistencia física de los rankings en el sistema de archivos.
"""

from __future__ import annotations
import json
import pathlib
from typing import Any, Dict, List, Optional

from domain.schemas import RankingResult

HISTORY_BASE_DIR = pathlib.Path("history")


def _ensure_history_dir() -> pathlib.Path:
    HISTORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_BASE_DIR


def build_run_manifest(
    ranking_result: RankingResult,
    artifacts: Dict[str, str],
    status: str = "success",
) -> Dict[str, Any]:
    return {
        "run_id": ranking_result.metadata.run_id,
        "generated_at": ranking_result.metadata.generated_at,
        "sector": ranking_result.metadata.sector,
        "company_type": ranking_result.metadata.company_type,
        "countries_requested": ranking_result.metadata.countries_requested,
        "total_countries": ranking_result.metadata.total_countries,
        "version": ranking_result.metadata.version,
        "status": status,
        "artifacts": artifacts,
    }


def save_ranking_run(
    ranking_result: RankingResult,
    artifact_paths: Dict[str, pathlib.Path],
    status: str = "success",
) -> pathlib.Path:
    _ensure_history_dir()
    run_id = ranking_result.metadata.run_id
    run_dir = HISTORY_BASE_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {key: str(path) for key, path in artifact_paths.items()}
    manifest = build_run_manifest(ranking_result, artifacts, status)

    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    with open(run_dir / "ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking_result.model_dump(), f, ensure_ascii=False, indent=2)

    return run_dir


def list_ranking_runs() -> List[Dict[str, Any]]:
    if not HISTORY_BASE_DIR.exists():
        return []
    runs = []
    for d in sorted(HISTORY_BASE_DIR.iterdir()):
        manifest_path = d / "manifest.json"
        if d.is_dir() and manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                runs.append(json.load(f))
    return runs


def load_ranking_run(run_id: str) -> Optional[Dict[str, Any]]:
    manifest_path = HISTORY_BASE_DIR / run_id / "manifest.json"
    if not manifest_path.exists():
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)
