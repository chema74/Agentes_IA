from __future__ import annotations

from services.vectorstore.base import VectorStoreBackend


class EvidenceRetriever:
    def __init__(self, store: VectorStoreBackend) -> None:
        self.store = store

    def search(self, query: str, top_k: int = 5):
        return self.store.search(query, top_k=top_k)

