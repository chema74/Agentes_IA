from __future__ import annotations

from connectors.files.loader import load_bytes
from services.parsing.parser import parse_loaded_file


def test_parse_txt_log_classifies_log():
    loaded = load_bytes("auth.log.txt", b"2026-01-01 INFO ok\n2026-01-01 ERROR broken")
    text, meta = parse_loaded_file(loaded, redact=True)
    assert "ERROR broken" in text
    assert meta["classification"] == "log"
    assert meta["has_errors"] is True


def test_parse_csv_ticket_export_detects_ticket_count():
    csv_bytes = b"ticket_id,status,priority\nINC-1,open,high\nINC-2,closed,low\n"
    loaded = load_bytes("tickets.csv", csv_bytes)
    _, meta = parse_loaded_file(loaded)
    assert meta["classification"] == "ticket_export"
    assert meta["ticket_count"] == 2


def test_parse_image_reference_is_allowed_without_text():
    loaded = load_bytes("diagram.png", b"fake-image")
    text, meta = parse_loaded_file(loaded)
    assert text == ""
    assert meta["classification"] == "image_reference"
    assert meta["sufficiency_status"] == "sufficient"
