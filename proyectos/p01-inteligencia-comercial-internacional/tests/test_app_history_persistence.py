from app import streamlit_app
from domain import history
from domain.dashboard import build_dashboard_rows, load_historical_rankings


def test_save_ranking_history_creates_run_files(tmp_path, monkeypatch):
    history_dir = tmp_path / "history"
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)

    resultados = [
        {
            "pais": "México",
            "score": 4.2,
            "resultado": {
                "resumen_ejecutivo": "Resumen México",
                "scores": {"riesgo_politico": 4.0},
                "fuentes": [{"categoria": "economico", "titulo": "Fuente MX"}],
            },
        },
        {
            "pais": "Alemania",
            "score": 3.1,
            "resultado": {
                "resumen_ejecutivo": "Resumen Alemania",
                "scores": {"riesgo_politico": 2.0},
                "fuentes": [],
            },
        },
    ]

    run_id = streamlit_app._save_ranking_history(
        resultados_ordenados=resultados,
        sector="Tecnología",
        tipo_empresa="PYME",
        countries_requested=["México", "Alemania"],
    )

    assert run_id is not None
    assert (history_dir / run_id / "manifest.json").exists()
    assert (history_dir / run_id / "ranking.json").exists()


def test_save_ranking_history_is_visible_in_dashboard_loader(tmp_path, monkeypatch):
    history_dir = tmp_path / "history"
    monkeypatch.setattr(history, "HISTORY_BASE_DIR", history_dir)

    resultados = [
        {
            "pais": "México",
            "score": 4.2,
            "resultado": {
                "resumen_ejecutivo": "Resumen México",
                "scores": {"riesgo_politico": 4.0, "riesgo_comercial": 5.0},
                "fuentes": [{"categoria": "economico", "titulo": "Fuente MX"}],
            },
        }
    ]

    streamlit_app._save_ranking_history(
        resultados_ordenados=resultados,
        sector="Tecnología",
        tipo_empresa="PYME",
        countries_requested=["México"],
    )

    payload = load_historical_rankings()
    rows = build_dashboard_rows(payload)

    assert len(rows) == 1
    assert rows[0]["country"] == "México"
    assert rows[0]["num_sources"] == 1
