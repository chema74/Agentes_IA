from __future__ import annotations

from pydantic import BaseModel, Field

from domain.plans.models import RecoveryOption
from domain.tasks.models import DisruptionEvent, LogisticsTask


class BreakerDecision(BaseModel):
    status: str
    reason_codes: list[str] = Field(default_factory=list)
    human_review_required: bool
    notes: list[str] = Field(default_factory=list)


def evaluate_logistics_breaker(task: LogisticsTask, disruption: DisruptionEvent, option: RecoveryOption | None) -> BreakerDecision:
    if option is None:
        return BreakerDecision(status="BLOCKED", reason_codes=["NO_RECOVERY_OPTION"], human_review_required=True, notes=["No existe capacidad verificada."])
    reasons: list[str] = []
    if option.missing_critical_data:
        reasons.append("INSUFFICIENT_DATA")
    if option.incremental_cost > task.authorized_incremental_cost:
        reasons.append("COST_THRESHOLD_EXCEEDED")
    if option.regulatory_compliant is False or option.operationally_feasible is False:
        reasons.append("COMPLIANCE_OR_OPERATIONAL_VIOLATION")
    if task.service_tier.lower() == "strategic" and option.projected_sla_breach_minutes > task.max_sla_breach_tolerance_minutes:
        reasons.append("STRATEGIC_SERVICE_DEGRADATION")
    if disruption.severity in {"critical", "high"} and option.confidence_score < 0.5:
        reasons.append("LOW_CONFIDENCE_RECOVERY")
    if reasons:
        return BreakerDecision(status="BLOCKED", reason_codes=reasons, human_review_required=True, notes=["El Logistics Circuit Breaker veta la autoejecucion."])
    if option.requires_human_approval:
        return BreakerDecision(status="PENDING_REVIEW", reason_codes=["MANUAL_APPROVAL_REQUIRED"], human_review_required=True, notes=["La alternativa requiere aprobacion humana."])
    return BreakerDecision(status="APPROVED", human_review_required=False, notes=["La alternativa cumple mandato y governance."])
