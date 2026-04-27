from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from domain.agent_cards.models import AgentCard
from domain.auctions.models import Bid, BidAuction
from domain.negotiation.models import NegotiationEvent
from domain.tasks.models import DisruptionEvent, LogisticsTask


class A2ANegotiator:
    def open_auction(self, task: LogisticsTask, disruption: DisruptionEvent, peers: list[AgentCard]) -> BidAuction:
        auction = BidAuction(
            auction_id=f"auction-{uuid4().hex[:10]}",
            task_id=task.id,
            bid_deadline=datetime.now(UTC) + timedelta(minutes=15),
            currency=task.currency,
            constraints_snapshot={
                "mode": task.mode,
                "required_capacity": task.capacity_required,
                "authorized_incremental_cost": task.authorized_incremental_cost,
                "disruption_type": disruption.disruption_type,
            },
        )
        for peer in peers:
            if task.mode not in peer.supported_modes or peer.available_capacity < task.capacity_required or not peer.is_fresh():
                continue
            cost_multiplier = 1.10 if peer.pricing_model == "spot" else 1.18
            bid = Bid(
                agent_id=peer.agent_id,
                offered_capacity=task.capacity_required,
                offered_cost=round(task.base_cost * cost_multiplier, 2),
                currency=task.currency,
                estimated_activation_minutes=45 if "hot_shot" in peer.capabilities else 90,
                projected_total_delay_minutes=max(30, disruption.estimated_delay_minutes - 60),
                confidence_score=round(peer.historical_reliability, 2),
                regulatory_compliant=all(constraint in peer.compliance_declarations for constraint in task.regulatory_constraints) if task.regulatory_constraints else True,
                operationally_feasible=True,
            )
            auction.bids.append(bid)
            auction.negotiation_log.extend(
                [
                    NegotiationEvent(
                        id=f"neg-{uuid4().hex[:10]}",
                        auction_id=auction.auction_id,
                        agent_id=peer.agent_id,
                        event_type="BID_REQUESTED",
                        message=f"Request for alternative capacity for task {task.id}",
                        offered_capacity=0.0,
                        offered_cost=0.0,
                        currency=task.currency,
                    ),
                    NegotiationEvent(
                        id=f"neg-{uuid4().hex[:10]}",
                        auction_id=auction.auction_id,
                        agent_id=peer.agent_id,
                        event_type="BID_RECEIVED",
                        message=f"Bid received from {peer.agent_id}",
                        offered_capacity=bid.offered_capacity,
                        offered_cost=bid.offered_cost,
                        currency=bid.currency,
                    ),
                ]
            )
        auction.status = "completed"
        return auction


A2A_NEGOTIATOR = A2ANegotiator()
