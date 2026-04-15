from __future__ import annotations

from domain.evidence.models import Evidence


def search_evidence(evidence_items: list[Evidence], query: str, top_k: int = 5) -> list[Evidence]:
    tokens = [token for token in query.lower().split() if token]
    scored: list[tuple[int, Evidence]] = []
    for item in evidence_items:
        score = sum(item.normalized_text.lower().count(token) for token in tokens)
        if score:
            scored.append((score, item))
    return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:top_k]]
