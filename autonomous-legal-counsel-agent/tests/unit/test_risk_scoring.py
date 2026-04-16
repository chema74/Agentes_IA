from __future__ import annotations

from domain.clauses.models import ClauseMapEntry
from services.templates.template_repository import TEMPLATE_REPOSITORY
from agents.risk_scoring_analyst import score_risks_and_redlines


def test_unlimited_liability_is_blocking_risk():
    clause = ClauseMapEntry(
        clause_id="cl-1",
        title="Liability",
        clause_type="liability",
        text="Supplier shall have unlimited liability for all losses.",
        playbook_alignment="aligned",
    )
    risks, redlines = score_risks_and_redlines([clause], TEMPLATE_REPOSITORY.resolve_template("MSA"))
    assert any(item.deviation_type == "unlimited" for item in risks)
    assert redlines
