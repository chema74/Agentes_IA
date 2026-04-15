from __future__ import annotations

from pathlib import Path

from services.exports.exporter import export_csv, export_docx, export_json, export_markdown


def test_exports_create_files(tmp_path: Path) -> None:
    result = {
        "filename": "sample_contract.txt",
        "summary": {"executive_summary": "Summary"},
        "obligations": [{"obligation_id": "1", "description": "Pay invoices", "responsible_party": "Buyer", "due_date": "2026-06-01", "confidence": 0.9}],
    }
    assert export_json(result, tmp_path / "out.json").exists()
    assert export_markdown(result, tmp_path / "out.md").exists()
    assert export_csv(result, tmp_path / "out.csv").exists()
    assert export_docx(result, tmp_path / "out.docx").exists()

