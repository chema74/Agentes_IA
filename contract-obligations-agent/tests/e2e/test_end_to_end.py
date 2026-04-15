from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_end_to_end_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("APP_EXPORT_DIR", str(tmp_path / "exports"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "data" / "chroma"))
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path / 'data' / 'contract_obligations.sqlite3'}")

    import importlib
    wf = importlib.reload(importlib.import_module("services.workflows.contract_workflow"))
    from services.exports.exporter import export_json

    content = (Path(__file__).resolve().parents[2] / "sample_data" / "contracts" / "sample_contract.txt").read_bytes()
    result = wf.analyze_contract_file("sample_contract.txt", content, ".txt", checklist_json=json.dumps({"items": ["payment terms", "renewal", "confidentiality"]}))
    export_path = export_json(result.model_dump(mode="json"), tmp_path / "result.json")
    assert export_path.exists()
    assert result.summary.executive_summary

