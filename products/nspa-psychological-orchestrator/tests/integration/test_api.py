from __future__ import annotations

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None

import pytest


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_health_endpoint():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
