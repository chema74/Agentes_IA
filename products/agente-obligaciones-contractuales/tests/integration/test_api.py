from __future__ import annotations

from pathlib import Path

import pytest


def test_fastapi_health_and_analyze(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("fastapi")
    pytest.importorskip("multipart")
    from fastapi.testclient import TestClient

    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("APP_EXPORT_DIR", str(tmp_path / "exports"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "data" / "chroma"))
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path / 'data' / 'contract_obligations.sqlite3'}")

    import importlib

    app_module = importlib.reload(importlib.import_module("app.main"))
    client = TestClient(app_module.app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    sample = Path(__file__).resolve().parents[2] / "sample_data" / "contracts" / "sample_contract.txt"
    with sample.open("rb") as fh:
        response = client.post(
            "/analyze",
            files={"file": ("sample_contract.txt", fh.read(), "text/plain")},
            data={"checklist_json": '{"items": ["payment terms"]}'},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "sample_contract.txt"
    assert payload["summary"]["executive_summary"]
