from __future__ import annotations

from uuid import uuid4

from domain.negotiation.models import NegotiationTrack


class A2ANegotiationCounsel:
    def negotiate(self, review_id: str, issue_key: str, counterparty_name: str, our_position: str, counterparty_response: str | None, audit_reference: str, round_number: int = 1) -> NegotiationTrack:
        return NegotiationTrack(
            track_id=f"track-{uuid4().hex[:10]}",
            review_id=review_id,
            issue_key=issue_key,
            round_number=round_number,
            counterparty_name=counterparty_name,
            our_position=our_position,
            allowed_concession_range="Use approved fallback only.",
            counterparty_response=counterparty_response,
            status="pending_counterparty" if counterparty_response is None else "counterparty_replied",
            audit_reference=audit_reference,
        )


A2A_COUNSEL = A2ANegotiationCounsel()
