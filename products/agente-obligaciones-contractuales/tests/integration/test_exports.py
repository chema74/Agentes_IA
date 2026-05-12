from __future__ import annotations

from pathlib import Path

from services.exports.exporter import export_bundle, export_csv, export_docx, export_json, export_markdown


def test_exports_create_files(tmp_path: Path) -> None:
    result = {
        "filename": "sample_contract.txt",
        "summary": {"executive_summary": "Summary", "key_points": ["Point 1", "Point 2"]},
        "obligations": [
            {
                "obligation_id": "1",
                "description": "Pay invoices",
                "responsible_party": "Buyer",
                "due_date": "2026-06-01",
                "dependency": "subject to approval",
                "status": "open",
                "confidence": 0.9,
            }
        ],
        "dates": [{"date": "2026-06-01", "context": "Payment due date", "category": "explicit"}],
        "retrieval_hits": [{"rank": 1, "source_label": "sample_contract.txt", "source_excerpt": "Payment is due within 30 days."}],
        "comparison": {"status": "ok", "matched": ["renewal"], "missing": ["payment"], "unverifiable": ["if applicable"]},
    }
    assert export_json(result, tmp_path / "out.json").exists()
    assert export_markdown(result, tmp_path / "out.md").exists()
    assert export_csv(result, tmp_path / "out.csv").exists()
    assert export_docx(result, tmp_path / "out.docx").exists()
    bundle = export_bundle(result, tmp_path / "bundle")
    assert bundle["json"].exists()
    assert bundle["markdown"].exists()
    assert bundle["csv"].exists()
    assert bundle["docx"].exists()
