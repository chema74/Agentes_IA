from __future__ import annotations

from pydantic import BaseModel


class RedlineSuggestion(BaseModel):
    redline_id: str
    clause_id: str
    original_text: str
    proposed_text: str
    fallback_source: str
    negotiability: str
    justification: str
    priority: str
