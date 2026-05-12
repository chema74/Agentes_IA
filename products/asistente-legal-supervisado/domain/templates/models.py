from __future__ import annotations

from pydantic import BaseModel, Field


class ContractTemplate(BaseModel):
    template_id: str
    contract_type: str
    allowed_jurisdictions: list[str]
    fallback_positions: dict[str, str] = Field(default_factory=dict)
    prohibited_terms: list[str] = Field(default_factory=list)
    liability_cap_policy: str
    required_clauses: list[str] = Field(default_factory=list)
