from __future__ import annotations

from uuid import uuid4

from domain.clauses.models import ClauseMapEntry


def extract_clause_map(text: str) -> list[ClauseMapEntry]:
    entries: list[ClauseMapEntry] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    types = {
        "confidential": "confidentiality",
        "liability": "liability",
        "jurisdiction": "jurisdiction",
        "governing law": "jurisdiction",
        "data": "data_transfer",
        "processor": "data_transfer",
        "terminate": "termination",
        "renew": "renewal",
    }
    for line in lines:
        lowered = line.lower()
        matched_type = next((value for key, value in types.items() if key in lowered), None)
        if matched_type is None:
            continue
        entries.append(
            ClauseMapEntry(
                clause_id=f"clause-{uuid4().hex[:10]}",
                title=line[:80],
                clause_type=matched_type,
                text=line,
                playbook_alignment="aligned",
            )
        )
    return entries
