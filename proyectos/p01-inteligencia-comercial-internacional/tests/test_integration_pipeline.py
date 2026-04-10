from pathlib import Path

from domain import exporters, history
from domain.dashboard import load_historical_rankings, build_dashboard_rows, compute_dashboard_metrics
from domain.schemas import RankingMetadata, RankingItem, RankingResult, SourceItem


def build_sample_ranking_result(run_id: str = "2026-04-06_150000") -> RankingResult:
    return RankingResult(
        metadata=RankingMetadata(
            run_id=run_id,
            generated_at="2026-04-06T15:00:00",
            sector="Tecnología",
            company_type="PYME exportadora",
            countries_requested=["México", "Colombia", "Chile"],
            total_countries=3,
            version="integration-test",
        ),
        ranking=[
            RankingItem(
                position=1,
                country="México",
                score_total=22.0,
                dimension_scores={
                    "riesgo_politico": 4.0,
                    "riesgo_comercial": 5.0,
                    "estabilidad_economica": 10.0,
                },
                executive_summary="México destaca por equilibrio entre oportunidad y riesgo.",
                sources=[
                    SourceItem(
                        category="economico",
                        title="Fuente México",
                        url="https://example.com/mx",
                        summary="Resumen México",
                    )
                ],
                raw_result={"pais": "México"},
            ),
            RankingItem(
                position=2,
                country="Chile",
                score_total=20.0,
                dimension_scores={
                    "riesgo_politico": 4.0,
                    "riesgo_comercial": 6.0,
                    "estabilidad_economica": 9.0,
                },
                executive_summary="Chile presenta estabilidad relativa.",
                sources=[],
                raw_result={"pais": "Chile"},
            ),
            RankingItem(
                position=3,
                country="Colombia",
                score_total=18.0,
                dimension_scores={
                    "riesgo_politico": 5.0,
                    "riesgo_comercial": 6.0,
                    "estabilidad_economica": 8.0,
                },
                executive_summary="Colombia ofrece potencial con cautelas.",
                sources=[],
                raw_result={"pais": "Colombia"},
            ),
        ],
    )


def test_full_ranking_pipeline_export_history_dashboard(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    history_dir = rankings_dir / "history"

    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)

    ranking_result = build_sample_ranking_result()

    json_path = exporters.export_ranking_to_json(ranking_result)
    csv_path = exporters.export_ranking_to_csv(ranking_result)
    md_path = exporters.export_ranking_to_markdown(ranking_result)
    docx_path = exporters.export_ranking_to_docx(ranking_result)

    assert json_path.exists()
    assert csv_path.exists()
    assert md_path.exists()
    assert docx_path.exists()

    run_dir = history.save_ranking_run(
        ranking_result=ranking_result,
        artifact_paths={
            "json": json_path,
            "csv": csv_path,
            "markdown": md_path,
            "docx": docx_path,
        },
    )

    assert run_dir.exists()
    assert (run_dir / "manifest.json").exists()

    runs = history.list_ranking_runs()
    assert len(runs) == 1
    assert runs[0]["run_id"] == ranking_result.metadata.run_id

    historical_rankings = load_historical_rankings()
    rows = build_dashboard_rows(historical_rankings)
    metrics = compute_dashboard_metrics(rows)

    assert len(rows) == 3
    assert metrics["total_runs"] == 1
    assert metrics["total_country_records"] == 3
    assert metrics["unique_countries"] == 3
    assert metrics["most_used_sector"] == "Tecnología"
    assert metrics["best_country_avg"] == "Colombia"


def test_full_ranking_pipeline_with_two_runs(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    history_dir = rankings_dir / "history"

    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)

    run_1 = build_sample_ranking_result(run_id="2026-04-06_150000")
    run_2 = build_sample_ranking_result(run_id="2026-04-07_160000")

    for ranking_result in [run_1, run_2]:
        json_path = exporters.export_ranking_to_json(ranking_result)
        csv_path = exporters.export_ranking_to_csv(ranking_result)
        md_path = exporters.export_ranking_to_markdown(ranking_result)
        docx_path = exporters.export_ranking_to_docx(ranking_result)

        history.save_ranking_run(
            ranking_result=ranking_result,
            artifact_paths={
                "json": json_path,
                "csv": csv_path,
                "markdown": md_path,
                "docx": docx_path,
            },
        )

    runs = history.list_ranking_runs()
    assert len(runs) == 2

    historical_rankings = load_historical_rankings()
    rows = build_dashboard_rows(historical_rankings)
    metrics = compute_dashboard_metrics(rows)

    assert len(rows) == 6
    assert metrics["total_runs"] == 2
    assert metrics["unique_countries"] == 3
