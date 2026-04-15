from __future__ import annotations

import hashlib
from collections import Counter
from math import sqrt

from domain.contracts.models import TextChunk
from services.vectorstore.base import SearchHit


def _hash_embedding(text: str, dims: int = 64) -> list[float]:
    vector = [0.0] * dims
    for token in text.lower().split():
        idx = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % dims
        vector[idx] += 1.0
    norm = sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


class _EmbeddingFunction:
    def __call__(self, input: list[str]) -> list[list[float]]:
        return [_hash_embedding(text) for text in input]


class ChromaVectorStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self._chunks: list[TextChunk] = []
        self._collection = None
        try:
            import chromadb

            client = chromadb.PersistentClient(path=path)
            self._collection = client.get_or_create_collection(
                name="contract_obligations",
                embedding_function=_EmbeddingFunction(),
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            self._collection = None

    def upsert(self, document_id: str, chunks: list[TextChunk]) -> None:
        self._chunks.extend(chunks)
        if self._collection is None:
            return
        self._collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "source_label": chunk.source_label,
                    "document_id": document_id,
                    "source_start": chunk.start_char,
                    "source_end": chunk.end_char,
                }
                for chunk in chunks
            ],
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        if self._collection is not None:
            results = self._collection.query(query_texts=[query], n_results=top_k)
            hits: list[SearchHit] = []
            for idx, chunk_id in enumerate(results.get("ids", [[]])[0]):
                metadata = results["metadatas"][0][idx]
                hits.append(
                    SearchHit(
                        chunk_id=chunk_id,
                        text=results["documents"][0][idx],
                        source_label=metadata.get("source_label", ""),
                        score=1.0 / (1.0 + float(results["distances"][0][idx])),
                        source_start=int(metadata.get("source_start", 0) or 0),
                        source_end=int(metadata.get("source_end", 0) or 0),
                        document_id=metadata.get("document_id", ""),
                    )
                )
            return hits

        terms = [t for t in query.lower().split() if t]
        scored: list[SearchHit] = []
        for chunk in self._chunks:
            score = sum(chunk.text.lower().count(term) for term in terms)
            if score:
                scored.append(
                    SearchHit(
                        chunk_id=chunk.chunk_id,
                        text=chunk.text,
                        source_label=chunk.source_label,
                        score=float(score),
                        source_start=chunk.start_char,
                        source_end=chunk.end_char,
                    )
                )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
