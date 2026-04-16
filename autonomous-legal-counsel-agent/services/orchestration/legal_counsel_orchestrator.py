from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from agents.clause_extraction_engine import extract_clause_map
from agents.document_intake_clerk import classify_contract
from agents.final_approval_governor import decide_approval
from agents.risk_scoring_analyst import score_risks_and_redlines
from core.audit.events import make_audit_event
from core.safety.legal_risk_breaker import evaluate_legal_breaker
from domain.contracts.models import ContractReview
from services.negotiation.a2a_counsel import A2A_COUNSEL
from services.storage.repositories import STORE
from services.templates.template_repository import TEMPLATE_REPOSITORY


class OrchestratorInput(BaseModel):
    contract_text: str
    counterparty_name: str = "counterparty"
    review_id: str | None = None
    issue_key: str | None = None
    counterparty_response: str | None = None


class OrchestratorOutput(BaseModel):
    contract_type: str
    clause_map: list[dict]
    risk_clauses: list[dict]
    redline_suggestions: list[dict]
    negotiation_status: str
    approval_recommendation: dict
    human_review_required: bool
    legal_notes: list[str]
    audit_reference: str
    review_id: str


class LegalCounselOrchestrator:
    def review(self, payload: OrchestratorInput) -> OrchestratorOutput:
        review_id = payload.review_id or f"review-{uuid4().hex[:10]}"
        contract_type = classify_contract(payload.contract_text)
        template = TEMPLATE_REPOSITORY.resolve_template(contract_type)
        clause_map = extract_clause_map(payload.contract_text)
        risks, redlines = score_risks_and_redlines(clause_map, template)
        breaker = evaluate_legal_breaker(risks)
        approval = decide_approval(risks, redlines, breaker.status)
        audit_reference = f"audit-ref-{uuid4().hex[:10]}"
        notes = [
            "Automated output does not replace final legal professional review in sensitive matters.",
            *breaker.notes,
        ]
        review = ContractReview(
            review_id=review_id,
            contract_type=contract_type,
            clause_map=clause_map,
            risk_clauses=risks,
            redline_suggestions=redlines,
            negotiation_status="not_started" if not redlines else "ready_for_negotiation",
            approval_recommendation=approval,
            human_review_required=breaker.human_review_required or approval.status != "APPROVABLE",
            legal_notes=notes,
            audit_reference=audit_reference,
        )
        STORE.save_review(review)
        self._append_event(audit_reference, "CONTRACT_REVIEW", review.review_id, "reviewed", {"contract_type": contract_type, "approval": approval.status})
        return self._output(review)

    def redline(self, payload: OrchestratorInput) -> OrchestratorOutput:
        return self.review(payload)

    def negotiate(self, payload: OrchestratorInput) -> OrchestratorOutput:
        base_review = self.review(payload)
        review = STORE.get_review(base_review.review_id)
        issue_key = payload.issue_key or (review.risk_clauses[0].category if review and review.risk_clauses else "general")
        if review is None:
            raise RuntimeError("Review not found after creation")
        track = A2A_COUNSEL.negotiate(
            review_id=review.review_id,
            issue_key=issue_key,
            counterparty_name=payload.counterparty_name,
            our_position="Use approved fallback wording only.",
            counterparty_response=payload.counterparty_response,
            audit_reference=review.audit_reference,
            round_number=len(review.negotiation_tracks) + 1,
        )
        review.negotiation_tracks.append(track)
        review.negotiation_status = track.status
        STORE.save_negotiation_track(track)
        STORE.save_review(review)
        self._append_event(review.audit_reference, "NEGOTIATION_TRACK", track.track_id, "negotiation_round", {"issue_key": issue_key, "status": track.status})
        return self._output(review)

    def _append_event(self, reference: str, entity_type: str, entity_id: str, action: str, payload: dict) -> None:
        STORE.append_audit_event(make_audit_event(reference, entity_type, entity_id, action, payload))

    def _output(self, review: ContractReview) -> OrchestratorOutput:
        return OrchestratorOutput(
            contract_type=review.contract_type,
            clause_map=[item.model_dump(mode="json") for item in review.clause_map],
            risk_clauses=[item.model_dump(mode="json") for item in review.risk_clauses],
            redline_suggestions=[item.model_dump(mode="json") for item in review.redline_suggestions],
            negotiation_status=review.negotiation_status,
            approval_recommendation=review.approval_recommendation.model_dump(mode="json"),
            human_review_required=review.human_review_required,
            legal_notes=review.legal_notes,
            audit_reference=review.audit_reference,
            review_id=review.review_id,
        )


ORCHESTRATOR = LegalCounselOrchestrator()
