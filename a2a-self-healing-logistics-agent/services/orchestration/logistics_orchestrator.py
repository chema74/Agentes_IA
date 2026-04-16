from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel

from agents.disruption_monitor import assess_disruption
from agents.negotiation_swarm import build_recovery_options
from agents.peer_discovery_engine import summarize_discovery
from agents.recovery_executor import execute_selected_plan
from agents.sla_guardian import assess_sla_risk
from core.audit.events import make_audit_event
from core.safety.logistics_breaker import evaluate_logistics_breaker
from domain.plans.models import RecoveryOption, RecoveryPlan
from domain.tasks.models import DisruptionEvent, LogisticsTask
from services.discovery.a2a_registry import A2A_REGISTRY
from services.llm.groq_client import GROQ_CLIENT
from services.negotiation.a2a_negotiator import A2A_NEGOTIATOR
from services.storage.repositories import STORE


class OrchestratorInput(BaseModel):
    task: LogisticsTask
    disruption: DisruptionEvent
    recovery_plan_id: str | None = None


class OrchestratorOutput(BaseModel):
    disruption_status: str
    affected_tasks: list[dict]
    peer_discovery_summary: dict
    negotiation_results: dict
    sla_risk: str
    selected_recovery_plan: dict
    execution_status: str
    human_review_required: bool
    justification: str
    audit_reference: str


class LogisticsOrchestrator:
    def evaluate(self, payload: OrchestratorInput) -> OrchestratorOutput:
        STORE.tasks[payload.task.id] = payload.task
        disruption = assess_disruption(payload.task, payload.disruption)
        cards = A2A_REGISTRY.fetch_agent_cards()
        discovery_summary = summarize_discovery(payload.task, cards)
        viable_cards = [card for card in cards if card.agent_id in discovery_summary["peer_ids"]]
        auction = A2A_NEGOTIATOR.open_auction(payload.task, payload.disruption, viable_cards)
        STORE.auctions[auction.auction_id] = auction
        options = build_recovery_options(payload.task, auction.bids)
        selected_option = self._select_option(options)
        breaker = evaluate_logistics_breaker(payload.task, payload.disruption, selected_option)
        sla_risk = assess_sla_risk(payload.task, options)
        audit_reference = f"audit-ref-{uuid4().hex[:10]}"
        plan = RecoveryPlan(
            plan_id=f"plan-{uuid4().hex[:10]}",
            task_id=payload.task.id,
            disruption_summary=payload.disruption.summary,
            evaluated_options=options,
            selected_option=selected_option,
            selected_option_rationale=GROQ_CLIENT.explain_selection(
                selected_agent_id=selected_option.agent_id if selected_option else None,
                options_count=len(options),
                status=breaker.status,
            ),
            sla_risk=sla_risk,
            status=breaker.status,
            audit_reference=audit_reference,
        )
        STORE.recovery_plans[plan.plan_id] = plan
        self._append_audit_snapshot(audit_reference, payload.task, auction.auction_id, plan)
        return OrchestratorOutput(
            disruption_status=disruption["disruption_status"],
            affected_tasks=[payload.task.model_dump(mode="json")],
            peer_discovery_summary=discovery_summary,
            negotiation_results={
                "auction_id": auction.auction_id,
                "bid_count": len(auction.bids),
                "events_logged": len(auction.negotiation_log),
                "bids": [bid.model_dump(mode="json") for bid in auction.bids],
            },
            sla_risk=sla_risk,
            selected_recovery_plan=plan.model_dump(mode="json"),
            execution_status="not_executed",
            human_review_required=breaker.human_review_required,
            justification=plan.selected_option_rationale,
            audit_reference=audit_reference,
        )

    def execute(self, payload: OrchestratorInput) -> OrchestratorOutput:
        evaluation = self.evaluate(payload)
        plan = STORE.recovery_plans[evaluation.selected_recovery_plan["plan_id"]]
        if payload.recovery_plan_id and payload.recovery_plan_id in STORE.recovery_plans:
            plan = STORE.recovery_plans[payload.recovery_plan_id]
        execution_status = "blocked"
        if plan.status == "APPROVED":
            evidence = execute_selected_plan(plan)
            plan.execution_evidence.extend(evidence)
            execution_status = "executed"
            self._append_event(plan.audit_reference, "RECOVERY_PLAN", plan.plan_id, "executed", {"evidence": evidence})
        else:
            self._append_event(plan.audit_reference, "RECOVERY_PLAN", plan.plan_id, "execution_blocked", {"status": plan.status})
        STORE.recovery_plans[plan.plan_id] = plan
        return OrchestratorOutput(
            disruption_status=evaluation.disruption_status,
            affected_tasks=evaluation.affected_tasks,
            peer_discovery_summary=evaluation.peer_discovery_summary,
            negotiation_results=evaluation.negotiation_results,
            sla_risk=plan.sla_risk,
            selected_recovery_plan=plan.model_dump(mode="json"),
            execution_status=execution_status,
            human_review_required=plan.status != "APPROVED",
            justification=plan.selected_option_rationale,
            audit_reference=plan.audit_reference,
        )

    def _select_option(self, options: list[RecoveryOption]) -> RecoveryOption | None:
        if not options:
            return None
        ranked = sorted(options, key=lambda item: item.score, reverse=True)
        top = ranked[0]
        if len(ranked) > 1 and abs(top.score - ranked[1].score) < 0.03:
            top.requires_human_approval = True
            top.tradeoffs.append("Material tie with alternative peer.")
        return top

    def _append_audit_snapshot(self, reference: str, task: LogisticsTask, auction_id: str, plan: RecoveryPlan) -> None:
        self._append_event(reference, "LOGISTICS_TASK", task.id, "evaluated", {"shipment_reference": task.shipment_reference})
        self._append_event(reference, "BID_AUCTION", auction_id, "completed", {"bid_count": len(plan.evaluated_options)})
        self._append_event(reference, "RECOVERY_PLAN", plan.plan_id, "created", {"status": plan.status})

    def _append_event(self, reference: str, entity_type: str, entity_id: str, action: str, payload: dict) -> None:
        STORE.append_audit_event(make_audit_event(reference, entity_type, entity_id, action, payload))


ORCHESTRATOR = LogisticsOrchestrator()
