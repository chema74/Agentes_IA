from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


def _headers() -> dict:
    return {"X-API-Key": "change-dev-key"}


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_evaluate_returns_required_contract():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/change-cases/evaluate",
        json={
            "process_notes": "Hay ambiguedad sobre prioridades. El equipo muestra fatiga y retrasos.",
            "context_type": "organizational",
        },
        headers=_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    for key in [
        "estado_del_proceso_de_cambio",
        "resumen_de_senales_detectadas",
        "mapa_de_stakeholders_o_contexto_personal",
        "perfil_de_resistencia",
        "bloqueos_de_adopcion_detectados",
        "nivel_de_friccion",
        "plan_de_intervencion",
        "hitos_de_transformacion",
        "alerta_de_fatiga_de_cambio",
        "revision_humana_requerida",
        "estado_de_la_puerta_de_supervision_humana",
        "recomendacion_final",
        "referencia_de_auditoría",
    ]:
        assert key in body


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_intervene_persists_case():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/change-cases/intervene",
        json={"process_notes": "Hay retrasos constantes y conflicto entre lider y equipo.", "context_type": "organizational"},
        headers=_headers(),
    )
    body = response.json()
    saved = client.get(f"/api/change-cases/{body['case_id']}", headers=_headers())
    audit = client.get(f"/api/audit/{body['referencia_de_auditoría']}", headers=_headers())
    assert response.status_code == 200
    assert saved.status_code == 200
    assert audit.status_code == 200


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_level_four_case_requires_human_review():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/change-cases/evaluate",
        json={"process_notes": "Existe fatiga muy alta. Hay bloqueo operativo y conflicto interpersonal.", "context_type": "organizational"},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["revision_humana_requerida"] is True


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_api_requires_key():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/change-cases/evaluate", json={"process_notes": "test", "context_type": "individual"})
    assert response.status_code == 401
