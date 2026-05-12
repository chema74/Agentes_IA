from __future__ import annotations

from pydantic import BaseModel, Field

from domain.risks.models import RiskClause


class LegalBreakerDecision(BaseModel):
    status: str
    reason_codes: list[str] = Field(default_factory=list)
    human_review_required: bool
    notes: list[str] = Field(default_factory=list)


def evaluate_legal_breaker(risk_clauses: list[RiskClause]) -> LegalBreakerDecision:
    reasons: list[str] = []
    for clause in risk_clauses:
        lowered = clause.category.lower()
        if clause.severity == "critical":
            reasons.append("PROHIBITED_OR_CRITICAL_CLAUSE")
        if lowered == "jurisdiction" and clause.severity in {"high", "critical"}:
            reasons.append("UNACCEPTABLE_JURISDICTION")
        if lowered == "liability" and clause.deviation_type == "unlimited":
            reasons.append("UNAUTHORIZED_UNLIMITED_LIABILITY")
        if lowered == "data_transfer" and clause.severity in {"high", "critical"}:
            reasons.append("INCOMPATIBLE_DATA_TRANSFER")
    if reasons:
        return LegalBreakerDecision(
            status="BLOCKED",
            reason_codes=sorted(set(reasons)),
            human_review_required=True,
            notes=["El Legal Risk Circuit Breaker detiene la aceptacion automatica."],
        )
    if any(clause.severity == "high" for clause in risk_clauses):
        return LegalBreakerDecision(
            status="NEGOTIABLE",
            reason_codes=["HIGH_RISK_RENEGOTIATION_REQUIRED"],
            human_review_required=True,
            notes=["El documento puede renegociarse, pero no avanzar sin control humano."],
        )
    return LegalBreakerDecision(
        status="APPROVABLE",
        human_review_required=False,
        notes=["No se detecto clausula prohibida ni riesgo no cubierto por playbook."],
    )
