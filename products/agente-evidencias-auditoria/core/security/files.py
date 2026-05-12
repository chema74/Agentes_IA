from __future__ import annotations

from pathlib import Path

from core.config.settings import settings


ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg"}


def validate_upload(filename: str, size_bytes: int) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")
    if size_bytes > settings.max_file_mb * 1024 * 1024:
        raise ValueError("File exceeds maximum size.")
