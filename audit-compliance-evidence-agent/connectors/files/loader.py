from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoadedFile:
    filename: str
    suffix: str
    content: bytes


def load_bytes(filename: str, content: bytes) -> LoadedFile:
    return LoadedFile(filename=filename, suffix=Path(filename).suffix.lower(), content=content)
