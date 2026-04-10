from domain.dashboard import (
    build_dashboard_rows,
    compute_dashboard_metrics,
    filter_dashboard_rows,
    get_filter_options,
    get_country_timeseries,
)


def build_sample_history_payload():
    return [
        {
            "manifest": {
                "run_id": "run_1",
                "generated_at": "2026-04-06T10:00:00",
                "sector": "Tecnología",
                "company_type": "PYME exportadora",
            },
            "ranking_data": {
                "metadata": {
                    "run_id": "run_1",
                    "generated_at": "2026-04-06T10:00:00",
                    "sector": "Tecnología",
                    "company_type": "PYME exportadora",
                },
                "ranking": [
                    {
                        "position": 1,
                        "country": "México",
                        "score_total": 22,
                        "executive_summary": "Resumen México",
                        "sources": [{"a": 1}, {"a": 2}],
                        "dimension_scores": {
                            "riesgo_politico": 4,
                            "riesgo_comercial": 5,
                            "estabilidad_economica": 10,
                        },
                    },
                    {
                        "position": 2,
                        "country": "Colombia",
                        "score_total": 19,
                        "executive_summary": "Resumen Colombia",
                        "sources": [{"a": 1}],
                        "dimension_scores": {
                            "riesgo_politico": 5,
                            "riesgo_comercial": 6,
                            "estabilidad_economica": 8,
                        },
                    },
                ],
            },
        },
        {
            "manifest": {
                "run_id": "run_2",
                "generated_at": "2026-04-07T10:00:00",
                "sector": "Tecnología",
                "company_type": "PYME exportadora",
            },
            "ranking_data": {
                "metadata": {
                    "run_id": "run_2",
                    "generated_at": "2026-04-07T10:00:00",
                    "sector": "Tecnología",
                    "company_type": "PYME exportadora",
                },
                "ranking": [
                    {
                        "position": 1,
                        "country": "México",
                        "score_total": 23,
                        "executive_summary": "Resumen México 2",
                        "sources": [{"a": 1}],
                        "dimension_scores": {
                            "riesgo_politico": 3,
                            "riesgo_comercial": 5,
                            "estabilidad_economica": 10,
                        },
                    },
                    {
                        "position": 2,
                        "country": "Chile",
                        "score_total": 20,
                        "executive_summary": "Resumen Chile",
                        "sources": [],
                        "dimension_scores": {
                            "riesgo_politico": 4,
                            "riesgo_comercial": 6,
                            "estabilidad_economica": 9,
                        },
                    },
                ],
            },
        },
    ]


def test_build_dashboard_rows():
    rows = build_dashboard_rows(build_sample_history_payload())

    assert len(rows) == 4
    assert rows[0]["country"] == "México"
    assert "score_total" in rows[0]
    assert "num_sources" in rows[0]
    assert "riesgo_politico" in rows[0]


def test_compute_dashboard_metrics():
    rows = build_dashboard_rows(build_sample_history_payload())
    metrics = compute_dashboard_metrics(rows)

    assert metrics["total_runs"] == 2
    assert metrics["total_country_records"] == 4
    assert metrics["unique_countries"] == 3
    assert metrics["most_used_sector"] == "Tecnología"
    assert metrics["best_country_avg"] == "Colombia"


def test_filter_dashboard_rows():
    rows = build_dashboard_rows(build_sample_history_payload())

    filtered = filter_dashboard_rows(
        rows=rows,
        country="México",
        sector="Tecnología",
        company_type="PYME exportadora",
    )

    assert len(filtered) == 2
    assert all(row["country"] == "México" for row in filtered)


def test_get_filter_options():
    rows = build_dashboard_rows(build_sample_history_payload())
    options = get_filter_options(rows)

    assert "Todos" in options["countries"]
    assert "México" in options["countries"]
    assert "Tecnología" in options["sectors"]
    assert "PYME exportadora" in options["company_types"]


def test_get_country_timeseries():
    rows = build_dashboard_rows(build_sample_history_payload())
    timeseries = get_country_timeseries(rows, "México")

    assert len(timeseries) == 2
    assert timeseries[0]["generated_at"] == "2026-04-06T10:00:00"
    assert timeseries[1]["generated_at"] == "2026-04-07T10:00:00"
    assert timeseries[1]["score_total"] == 23
