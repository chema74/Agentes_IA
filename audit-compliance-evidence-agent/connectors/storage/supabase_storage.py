from __future__ import annotations

from pathlib import Path

from core.config.settings import settings


class SupabaseStorageAdapter:
    def __init__(self) -> None:
        self.base_dir = settings.data_dir / "storage"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, bucket: str, relative_path: str, content: bytes) -> str:
        path = self.base_dir / bucket / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    def read(self, storage_path: str) -> bytes:
        return Path(storage_path).read_bytes()
