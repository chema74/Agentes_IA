from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.contracts.models import TextChunk


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    text: str
    source_label: str
    score: float
    source_start: int = 0
    source_end: int = 0
    document_id: str = ""


class VectorStoreBackend(Protocol):
    def upsert(self, document_id: str, chunks: list[TextChunk]) -> None: ...
    def search(self, query: str, top_k: int = 5) -> list[SearchHit]: ...
