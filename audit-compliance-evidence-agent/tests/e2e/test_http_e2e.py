from __future__ import annotations

import pytest

pytest.importorskip("fastapi")


def test_api_and_web_flow_demo_login_and_health():
    multipart = pytest.importorskip("multipart")
    assert multipart is not None

    from fastapi.testclient import TestClient
    from app.main import app
    from scripts.seed_mock_data import reset_store, seed_demo_data

    reset_store()
    seed_demo_data(reset=False)
    client = TestClient(app)

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    login = client.post("/api/auth/login", json={"email": "compliance@example.com", "password": "demo"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    scopes = client.get("/api/scopes", headers={"Authorization": f"Bearer {token}"})
    assert scopes.status_code == 200
    assert scopes.json()
