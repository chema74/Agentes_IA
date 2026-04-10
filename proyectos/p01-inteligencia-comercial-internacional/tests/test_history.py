from domain import history
from domain.schemas import RankingMetadata, RankingItem, RankingResult, SourceItem


def build_sample_ranking_result() -> RankingResult:
    return RankingResult(
        metadata=RankingMetadata(
            run_id="2026-04-06_120000",
            generated_at="2026-04-06T12:00:00",
            sector="Tecnología",
            company_type="PYME exportadora",
            countries_requested=["México", "Colombia"],
            total_countries=2,
            version="test",
        ),
        ranking=[
            RankingItem(
                position=1,
                country="México",
                score_total=21.0,
                dimension_scores={
                    "riesgo_politico": 4.0,
                    "riesgo_comercial": 5.0,
                    "estabilidad_economica": 9.0,
                },
                executive_summary="Resumen México",
                sources=[
                    SourceItem(
                        category="politico",
                        title="Fuente México",
                        url="https://example.com/mx",
                        summary="Resumen fuente mx",
                    )
                ],
                raw_result={
                    "pais": "México",
                    "scores": {
                        "riesgo_politico": 4.0,
                        "riesgo_comercial": 5.0,
                        "estabilidad_economica": 9.0,
                    },
                    "fuentes": [
                        {
                            "categoria": "politico",
                            "titulo": "Fuente México",
                            "url": "https://example.com/mx",
                            "resumen": "Resumen fuente mx",
                        }
                    ],
                },
            ),
            RankingItem(
                position=2,
                country="Colombia",
                score_total=18.0,
                dimension_scores={
                    "riesgo_politico": 5.0,
                    "riesgo_comercial": 6.0,
                    "estabilidad_economica": 8.0,
                },
                executive_summary="Resumen Colombia",
                sources=[],
                raw_result={
                    "pais": "Colombia",
                    "scores": {
                        "riesgo_politico": 5.0,
                        "riesgo_comercial": 6.0,
                        "estabilidad_economica": 8.0,
                    },
                    "fuentes": [],
                },
            ),
        ],
    )


def test_build_run_manifest():
    ranking_result = build_sample_ranking_result()

    manifest = history.build_run_manifest(
        ranking_result=ranking_result,
        artifacts={
            "json": "a.json",
            "csv": "a.csv",
        },
        status="success",
    )

    assert manifest["run_id"] == "2026-04-06_120000"
    assert manifest["sector"] == "Tecnología"
    assert manifest["company_type"] == "PYME exportadora"
    assert manifest["total_countries"] == 2
    assert manifest["status"] == "success"
    assert manifest["artifacts"]["json"] == "a.json"


def test_save_ranking_run_and_list_runs(tmp_path, monkeypatch):
    history_dir = tmp_path / "history"
    history_db_path = tmp_path / "data" / "history.sqlite3"
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)
    monkeypatch.setattr(history, "HISTORY_DB_PATH", history_db_path)

    ranking_result = build_sample_ranking_result()

    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    json_file = artifacts_dir / "ranking.json"
    csv_file = artifacts_dir / "ranking.csv"
    md_file = artifacts_dir / "ranking.md"
    docx_file = artifacts_dir / "ranking.docx"

    json_file.write_text("{}", encoding="utf-8")
    csv_file.write_text("a,b\n1,2\n", encoding="utf-8")
    md_file.write_text("# test", encoding="utf-8")
    docx_file.write_bytes(b"fake-docx")

    run_dir = history.save_ranking_run(
        ranking_result=ranking_result,
        artifact_paths={
            "json": json_file,
            "csv": csv_file,
            "markdown": md_file,
            "docx": docx_file,
        },
    )

    assert run_dir.exists()
    assert (run_dir / "manifest.json").exists()
    assert history_db_path.exists()

    runs = history.list_ranking_runs()
    assert len(runs) == 1
    assert runs[0]["run_id"] == "2026-04-06_120000"
    assert runs[0]["status"] == "success"


def test_load_ranking_run(tmp_path, monkeypatch):
    history_dir = tmp_path / "history"
    history_db_path = tmp_path / "data" / "history.sqlite3"
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)
    monkeypatch.setattr(history, "HISTORY_DB_PATH", history_db_path)

    ranking_result = build_sample_ranking_result()

    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    json_file = artifacts_dir / "ranking.json"
    json_file.write_text("{}", encoding="utf-8")

    run_dir = history.save_ranking_run(
        ranking_result=ranking_result,
        artifact_paths={"json": json_file},
    )

    loaded = history.load_ranking_run("2026-04-06_120000")

    assert run_dir.exists()
    assert loaded["run_id"] == "2026-04-06_120000"
    assert loaded["sector"] == "Tecnología"
    assert loaded["total_countries"] == 2


def test_load_ranking_payload_from_sqlite_without_legacy_json(tmp_path, monkeypatch):
    history_dir = tmp_path / "history"
    history_db_path = tmp_path / "data" / "history.sqlite3"
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)
    monkeypatch.setattr(history, "HISTORY_DB_PATH", history_db_path)

    ranking_result = build_sample_ranking_result()

    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    json_file = artifacts_dir / "ranking.json"
    json_file.write_text("{}", encoding="utf-8")

    run_dir = history.save_ranking_run(
        ranking_result=ranking_result,
        artifact_paths={"json": json_file},
    )

    for legacy_file in run_dir.iterdir():
        legacy_file.unlink()
    run_dir.rmdir()

    payload = history.load_ranking_payload("2026-04-06_120000")

    assert payload is not None
    assert payload["manifest"]["run_id"] == "2026-04-06_120000"
    assert payload["ranking_data"]["metadata"]["sector"] == "Tecnología"
    assert len(payload["ranking_data"]["ranking"]) == 2
    assert payload["ranking_data"]["ranking"][0]["country"] == "México"
