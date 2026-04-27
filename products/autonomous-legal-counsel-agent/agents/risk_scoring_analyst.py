from __future__ import annotations

from uuid import uuid4

from domain.clauses.models import ClauseMapEntry
from domain.redlines.models import RedlineSuggestion
from domain.risks.models import RiskClause
from domain.templates.models import ContractTemplate
from services.llm.gemini_client import GEMINI_CLIENT
from services.playbooks.playbook_repository import PLAYBOOK_REPOSITORY


def score_risks_and_redlines(clause_map: list[ClauseMapEntry], template: ContractTemplate) -> tuple[list[RiskClause], list[RedlineSuggestion]]:
    risks: list[RiskClause] = []
    redlines: list[RedlineSuggestion] = []
    rules = PLAYBOOK_REPOSITORY.rules()
    for clause in clause_map:
        lowered = clause.text.lower()
        if clause.clause_type == "liability" and "unlimited liability" in lowered:
            risks.append(_risk(clause, "liability", "critical", "unlimited", "Unlimited liability is outside approved policy.", "Replace with approved cap."))
            redlines.append(_redline(clause, template.fallback_positions.get("liability", "Cap liability per approved policy."), "playbook-liability"))
        elif clause.clause_type == "jurisdiction" and any(term.lower() in lowered for term in rules["jurisdiction"]["forbidden"]):
            risks.append(_risk(clause, "jurisdiction", "critical", "forbidden_forum", "Jurisdiction is outside approved forum.", "Replace with EU venue."))
            redlines.append(_redline(clause, template.fallback_positions.get("jurisdiction", "EU venue only."), "playbook-jurisdiction"))
        elif clause.clause_type == "data_transfer" and ("outside eu" in lowered or "unrestricted transfer" in lowered):
            risks.append(_risk(clause, "data_transfer", "high", "incompatible_transfer", "Cross-border transfer is incompatible with policy.", "Use SCC or EU-only transfer."))
            redlines.append(_redline(clause, template.fallback_positions.get("data_transfer", "Use SCC or EU-only transfer."), "playbook-data"))
        elif clause.clause_type == "termination" and "for convenience" in lowered:
            risks.append(_risk(clause, "termination", "medium", "asymmetric", "Termination right appears asymmetric.", "Mutualize or narrow termination right."))
        clause.playbook_alignment = "deviated" if any(r.clause_id == clause.clause_id for r in risks) else "aligned"
    return risks, redlines


def _risk(clause: ClauseMapEntry, category: str, severity: str, deviation_type: str, reason: str, action: str) -> RiskClause:
    return RiskClause(
        risk_clause_id=f"risk-{uuid4().hex[:10]}",
        clause_id=clause.clause_id,
        category=category,
        severity=severity,
        playbook_rule_id=f"rule-{category}",
        deviation_type=deviation_type,
        risk_reason=reason,
        recommended_action=action,
        human_review_required=severity in {"high", "critical"},
    )


def _redline(clause: ClauseMapEntry, fallback_text: str, source: str) -> RedlineSuggestion:
    return RedlineSuggestion(
        redline_id=f"redline-{uuid4().hex[:10]}",
        clause_id=clause.clause_id,
        original_text=clause.text,
        proposed_text=GEMINI_CLIENT.propose_redline(clause.clause_type, clause.text, fallback_text),
        fallback_source=source,
        negotiability="NEGOTIABLE",
        justification=f"Fallback approved for {clause.clause_type}.",
        priority="high",
    )
