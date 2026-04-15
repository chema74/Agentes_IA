from __future__ import annotations

from domain.clauses.models import EvidenceRef
from domain.contracts.models import RetrievalHit
from services.vectorstore.base import VectorStoreBackend


class EvidenceRetriever:
    def __init__(self, store: VectorStoreBackend) -> None:
        self.store = store

    def search(self, query: str, top_k: int = 5) -> list[RetrievalHit]:
        hits = self.store.search(query, top_k=top_k)
        out: list[RetrievalHit] = []
        for rank, hit in enumerate(hits, start=1):
            evidence = EvidenceRef(
                source_id=hit.document_id or hit.chunk_id,
                source_label=hit.source_label,
                chunk_id=hit.chunk_id,
                source_excerpt=hit.text[:280],
                confidence=min(0.99, max(0.1, hit.score)),
            )
            out.append(
                RetrievalHit(
                    query=query,
                    rank=rank,
                    chunk_id=hit.chunk_id,
                    source_label=hit.source_label,
                    source_excerpt=hit.text[:280],
                    score=hit.score,
                    source_start=hit.source_start,
                    source_end=hit.source_end,
                    evidence=[evidence],
                )
            )
        return out
