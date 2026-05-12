from __future__ import annotations

from importlib import reload

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None

@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_request_id_header_is_exposed():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/health", headers={"X-Request-ID": "req-test-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-1"


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_rate_limit_can_be_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_RATE_LIMIT", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    import core.config.settings as settings_module

    reload(settings_module)
    import app.main as app_main_module

    reload(app_main_module)
    client = TestClient(app_main_module.app)
    first = client.get("/api/health")
    second = client.get("/api/health")
    assert first.status_code == 200
    assert second.status_code == 429
