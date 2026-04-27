from __future__ import annotations

from domain.contracts.models import TextChunk
from services.vectorstore.base import SearchHit


class QdrantVectorStore:
    def __init__(self, url: str, collection: str) -> None:
        self.url = url
        self.collection = collection

    def upsert(self, document_id: str, chunks: list[TextChunk]) -> None:
        raise NotImplementedError("Qdrant adapter is prepared but not activated in this build.")

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        raise NotImplementedError("Qdrant adapter is prepared but not activated in this build.")

