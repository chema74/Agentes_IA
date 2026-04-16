from __future__ import annotations

from pydantic import BaseModel


class ClauseMapEntry(BaseModel):
    clause_id: str
    title: str
    clause_type: str
    text: str
    playbook_alignment: str
