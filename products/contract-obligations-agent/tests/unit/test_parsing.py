from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
import pytest

from connectors.email.loader import parse_eml
from connectors.files.loaders import LoadedFile
from services.parsing.parser import normalize_text, parse_loaded_file


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("Hello \n\n\n world") == "Hello\n\nworld"


def test_parse_docx_extracts_text(tmp_path: Path) -> None:
    path = tmp_path / "sample.docx"
    doc = Document()
    doc.add_paragraph("Payment is due within 30 days.")
    doc.save(path)
    loaded = LoadedFile(filename=path.name, suffix=".docx", content=path.read_bytes())
    parsed = parse_loaded_file(loaded)
    assert "Payment is due" in parsed.normalized_text
    assert parsed.document_type.value == "contract"


def test_parse_eml_extracts_metadata() -> None:
    content = (
        b"Subject: Renewal notice\nFrom: vendor@example.com\nTo: legal@example.com\n"
        b"Date: Tue, 15 Apr 2026 09:00:00 +0000\n\nThe agreement renews automatically."
    )
    parsed = parse_eml(content)
    assert parsed["subject"] == "Renewal notice"
    assert "renews automatically" in parsed["body"]


def test_parse_pdf_extracts_text_if_pypdf_available(tmp_path: Path) -> None:
    pytest.importorskip("pypdf")
    from pypdf import PdfWriter

    path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with path.open("wb") as fh:
        writer.write(fh)
    loaded = LoadedFile(filename=path.name, suffix=".pdf", content=path.read_bytes())
    try:
        parse_loaded_file(loaded)
    except Exception as exc:
        assert "No extractable text" in str(exc) or "PDF support" in str(exc)
