from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class FileLoadError(RuntimeError):
    pass


@dataclass(frozen=True)
class LoadedFile:
    filename: str
    suffix: str
    content: bytes


def load_file(path: str | Path) -> LoadedFile:
    p = Path(path)
    if not p.exists():
        raise FileLoadError(f"File not found: {p}")
    content = p.read_bytes()
    if not content:
        raise FileLoadError(f"File is empty: {p.name}")
    return LoadedFile(filename=p.name, suffix=p.suffix.lower(), content=content)


def load_bytes(filename: str, suffix: str, content: bytes) -> LoadedFile:
    if not content:
        raise FileLoadError(f"File is empty: {filename}")
    return LoadedFile(filename=filename, suffix=suffix.lower(), content=content)
