from __future__ import annotations

from connectors.storage.supabase_storage import SupabaseStorageAdapter


class StorageService:
    def __init__(self) -> None:
        self.adapter = SupabaseStorageAdapter()

    def store_evidence(self, relative_path: str, content: bytes) -> str:
        return self.adapter.upload("evidence-files", relative_path, content)

    def store_package(self, relative_path: str, content: bytes) -> str:
        return self.adapter.upload("audit-packages", relative_path, content)
