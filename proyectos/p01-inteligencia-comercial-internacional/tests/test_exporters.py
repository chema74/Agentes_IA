from pathlib import Path

from domain import exporters
from domain.schemas import RankingMetadata, RankingItem, RankingResult, SourceItem


def build_sample_ranking_result() -> RankingResult:
    return RankingResult(
        metadata=RankingMetadata(
            run_id="2026-04-06_130000",
            generated_at="2026-04-06T13:00:00",
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
                score_total=22.0,
                dimension_scores={
                    "riesgo_politico": 4.0,
                    "riesgo_comercial": 5.0,
                    "estabilidad_economica": 10.0,
                },
                executive_summary="Resumen México",
                sources=[
                    SourceItem(
                        category="economico",
                        title="Fuente 1",
                        url="https://example.com/1",
                        summary="Resumen 1",
                    )
                ],
                raw_result={"pais": "México"},
            ),
            RankingItem(
                position=2,
                country="Colombia",
                score_total=19.0,
                dimension_scores={
                    "riesgo_politico": 5.0,
                    "riesgo_comercial": 6.0,
                    "estabilidad_economica": 8.0,
                },
                executive_summary="Resumen Colombia",
                sources=[],
                raw_result={"pais": "Colombia"},
            ),
        ],
    )


def test_slugify_text():
    assert exporters.slugify_text("PYME exportadora") == "pyme_exportadora"
    assert exporters.slugify_text("Tecnología") == "tecnologia"
    assert exporters.slugify_text("  ") == "sin_valor"


def test_build_ranking_filename(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)

    path = exporters.build_ranking_filename(
        sector="Tecnología",
        company_type="PYME exportadora",
        extension="json",
        run_id="2026-04-06_130000",
    )

    assert path.parent == rankings_dir
    assert path.name.endswith(".json")
    assert "2026-04-06_130000" in path.name
    assert "tecnologia" in path.name
    assert "pyme_exportadora" in path.name


def test_flatten_ranking_for_csv():
    ranking_result = build_sample_ranking_result()
    rows = exporters.flatten_ranking_for_csv(ranking_result)

    assert len(rows) == 2
    assert rows[0]["country"] == "México"
    assert rows[0]["score_total"] == 22.0
    assert "score_riesgo_politico" in rows[0]
    assert rows[0]["sources_count"] == 1


def test_build_ranking_markdown_report():
    ranking_result = build_sample_ranking_result()
    content = exporters.build_ranking_markdown_report(ranking_result)

    assert "# Ranking de Riesgo País" in content
    assert "México" in content
    assert "Colombia" in content
    assert "Resumen México" in content
    assert "Fuente 1" in content


def test_export_ranking_to_json(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)

    ranking_result = build_sample_ranking_result()
    path = exporters.export_ranking_to_json(ranking_result)

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "México" in content
    assert "Colombia" in content


def test_export_ranking_to_csv(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)

    ranking_result = build_sample_ranking_result()
    path = exporters.export_ranking_to_csv(ranking_result)

    assert path.exists()
    content = path.read_text(encoding="utf-8-sig")
    assert "country" in content
    assert "México" in content
    assert "Colombia" in content


def test_export_ranking_to_markdown(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)

    ranking_result = build_sample_ranking_result()
    path = exporters.export_ranking_to_markdown(ranking_result)

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "# Ranking de Riesgo País" in content
    assert "Resumen Colombia" in content


def test_export_ranking_to_docx(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    monkeypatch.setattr(exporters, "RANKINGS_OUTPUT_DIR", rankings_dir)

    ranking_result = build_sample_ranking_result()
    path = exporters.export_ranking_to_docx(ranking_result)

    assert path.exists()
    assert path.suffix == ".docx"
    assert path.stat().st_size > 0