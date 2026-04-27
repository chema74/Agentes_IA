from __future__ import annotations

from pydantic import BaseModel


class ReviewPayload(BaseModel):
    contract_text: str
    counterparty_name: str = "counterparty"


class NegotiatePayload(BaseModel):
    contract_text: str
    counterparty_name: str = "counterparty"
    issue_key: str | None = None
    counterparty_response: str | None = None
