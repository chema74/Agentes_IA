from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


def _load_workflow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("APP_EXPORT_DIR", str(tmp_path / "exports"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "data" / "chroma"))
    monkeypatch.setenv("DB_URL", f"sqlite:///{tmp_path / 'data' / 'contract_obligations.sqlite3'}")
    import importlib

    module = importlib.import_module("services.workflows.contract_workflow")
    return importlib.reload(module)


def test_analyze_contract_extracts_obligations_and_alerts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wf = _load_workflow(tmp_path, monkeypatch)
    content = (Path(__file__).resolve().parents[2] / "sample_data" / "contracts" / "sample_contract.txt").read_bytes()
    result = wf.analyze_contract_file("sample_contract.txt", content, ".txt", checklist_json=json.dumps({"items": ["payment terms", "renewal"]}))
    assert result.clauses
    assert result.obligations
    assert result.summary.executive_summary
    assert result.comparison["status"] == "ok"


def test_high_risk_language_is_flagged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wf = _load_workflow(tmp_path, monkeypatch)
    content = b"Late payment may incur a penalty fee."
    result = wf.analyze_contract_file("risk.txt", content, ".txt", None)
    assert any(alert.severity.value == "high" for alert in result.alerts)

