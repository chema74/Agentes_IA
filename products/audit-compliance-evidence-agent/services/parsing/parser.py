from __future__ import annotations

import csv
import re
from io import BytesIO, StringIO

from connectors.files.loader import LoadedFile
from connectors.logs.parser import parse_log_lines
from connectors.tickets.parser import parse_ticket_csv
from core.security.redaction import redact_text


WHITESPACE_RE = re.compile(r"[ \t]+")
NEWLINES_RE = re.compile(r"\n{3,}")


def normalize_text(text: str, redact: bool = False) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = WHITESPACE_RE.sub(" ", text)
    text = NEWLINES_RE.sub("\n\n", text)
    text = text.strip()
    return redact_text(text) if redact else text


def classify_evidence(kind: str, text: str, metadata: dict) -> str:
    lowered = text.lower()
    if kind == "image_reference":
        return "image_reference"
    if metadata.get("ticket_count"):
        return "ticket_export"
    if "policy" in lowered or "politica" in lowered:
        return "policy"
    if "procedure" in lowered or "procedimiento" in lowered:
        return "procedure"
    if metadata.get("has_errors"):
        return "log"
    if kind == "csv":
        return "table"
    return kind


def parse_loaded_file(loaded: LoadedFile, redact: bool = False) -> tuple[str, dict]:
    suffix = loaded.suffix
    if suffix == ".txt":
        raw = loaded.content.decode("utf-8", errors="ignore")
        kind = "text"
        meta = {"source_kind": "text"}
    elif suffix == ".csv":
        raw = loaded.content.decode("utf-8", errors="ignore")
        rows = list(csv.DictReader(StringIO(raw)))
        kind = "csv"
        meta = {"row_count": len(rows), "source_kind": "csv"}
        if rows and {"ticket_id", "status"} <= set(rows[0].keys()):
            meta["ticket_count"] = len(parse_ticket_csv(raw))
    elif suffix == ".docx":
        try:
            from docx import Document
        except ImportError:
            raw = loaded.content.decode("utf-8", errors="ignore")
            kind = "document"
            meta = {"paragraph_count": 0, "source_kind": "docx", "parser_warning": "python-docx no disponible"}
        else:
            doc = Document(BytesIO(loaded.content))
            parts = [p.text for p in doc.paragraphs if p.text.strip()]
            raw = "\n".join(parts)
            kind = "document"
            meta = {"paragraph_count": len(parts), "source_kind": "docx"}
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raw = loaded.content.decode("utf-8", errors="ignore")
            kind = "document"
            meta = {"page_count": 0, "source_kind": "pdf", "parser_warning": "pypdf no disponible"}
        else:
            reader = PdfReader(BytesIO(loaded.content))
            raw = "\n\n".join(page.extract_text() or "" for page in reader.pages)
            kind = "document"
            meta = {"page_count": len(reader.pages), "source_kind": "pdf"}
    elif suffix in {".png", ".jpg", ".jpeg"}:
        raw = ""
        kind = "image_reference"
        meta = {"source_kind": "image_reference"}
    else:
        raw = loaded.content.decode("utf-8", errors="ignore")
        kind = "unknown"
        meta = {"source_kind": "unknown"}
    normalized = normalize_text(raw, redact=redact)
    if suffix == ".txt" and ("INFO" in raw or "ERROR" in raw):
        meta.update(parse_log_lines(raw))
        kind = "log"
    meta["classification"] = classify_evidence(kind, normalized, meta)
    meta["sufficiency_status"] = "insufficient" if not normalized and kind != "image_reference" else "sufficient"
    return normalized, meta
