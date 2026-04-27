from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


def _headers() -> dict:
    return {"X-API-Key": "trade-dev-key"}


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_evaluate_returns_required_contract():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/trade-cases/evaluate",
        json={"signal_text": "New sanctions and export controls affect this market.", "country": "Turkey", "sector": "industrial", "route": "Black Sea"},
        headers=_headers(),
    )
    body = response.json()
    assert response.status_code == 200
    for key in [
        "estado_de_la_señal_geopolítica",
        "resumen_del_perfil_de_riesgo_país",
        "mapa_de_exposición_comercial",
        "eventos_de_sanción_o_restricción_detectados",
        "alertas_de_disrupción_de_ruta",
        "nivel_de_riesgo_internacional",
        "escenarios_relevantes",
        "recomendación_operativa",
        "revisión_humana_requerida",
        "estado_de_la_puerta_de_revisión_humana",
        "memorando_de_decisión_exportadora",
        "referencia_de_auditoría",
    ]:
        assert key in body


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_significant_case_requires_human_review():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/trade-cases/evaluate",
        json={"signal_text": "New sanctions affect the route and export controls intensify.", "country": "Iran", "sector": "energy", "route": "Suez"},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["revisión_humana_requerida"] is True


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_assess_route_persists_case_and_audit():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/trade-cases/assess-route",
        json={"signal_text": "Port congestion and route disruption are increasing.", "country": "Egypt", "sector": "consumer", "route": "Suez"},
        headers=_headers(),
    )
    body = response.json()
    saved = client.get(f"/api/trade-cases/{body['case_id']}", headers=_headers())
    audit = client.get(f"/api/audit/{body['referencia_de_auditoría']}", headers=_headers())
    assert response.status_code == 200
    assert saved.status_code == 200
    assert audit.status_code == 200


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_api_requires_key():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/trade-cases/evaluate", json={"signal_text": "test", "country": "Spain", "sector": "food"})
    assert response.status_code == 401
