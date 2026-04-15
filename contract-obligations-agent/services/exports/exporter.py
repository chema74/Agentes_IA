from __future__ import annotations

import csv
import json
from pathlib import Path

from docx import Document


def export_json(result: dict, path: Path) -> Path:
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def export_markdown(result: dict, path: Path) -> Path:
    lines = [f"# {result['filename']}", "", "## Executive summary", result["summary"]["executive_summary"], "", "## Obligations"]
    lines.extend(f"- {item['description']}" for item in result.get("obligations", []))
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def export_csv(result: dict, path: Path) -> Path:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["obligation_id", "description", "responsible_party", "due_date", "confidence"])
        writer.writeheader()
        for item in result.get("obligations", []):
            writer.writerow({k: item.get(k, "") for k in writer.fieldnames})
    return path


def export_docx(result: dict, path: Path) -> Path:
    doc = Document()
    doc.add_heading(result["filename"], level=1)
    doc.add_heading("Executive summary", level=2)
    doc.add_paragraph(result["summary"]["executive_summary"])
    doc.add_heading("Obligations", level=2)
    for item in result.get("obligations", []):
        doc.add_paragraph(item["description"], style="List Bullet")
    doc.save(path)
    return path

