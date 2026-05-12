from __future__ import annotations

from pydantic import BaseModel


class ArchetypeProfile(BaseModel):
    dominant_archetype: str
    narrative_pattern: str
    symbolic_notes: str
