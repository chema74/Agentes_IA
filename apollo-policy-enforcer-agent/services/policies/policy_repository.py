from __future__ import annotations

from domain.policies.models import PolicyPredicate, PolicyRule
from services.storage.repositories import STORE


class PolicyRepository:
    def __init__(self) -> None:
        if not STORE.policies:
            self._seed()

    def _seed(self) -> None:
        spend_policy = PolicyRule(
            policy_id="policy-spend-threshold",
            name="Spend approval threshold",
            action_types=["approve_spend"],
            decision_on_failure="BLOCKED",
            priority=100,
            description="Blocking rule for spend above threshold without approver.",
            predicates=[
                PolicyPredicate(
                    predicate_id="pred-spend-under-limit",
                    name="spend_under_limit",
                    description="Amount must be under threshold or require explicit approval.",
                    predicate_type="threshold",
                    operator="<=",
                    expected_value=5000.0,
                    severity="high",
                    source_policy_id="policy-spend-threshold",
                    priority=100,
                ),
                PolicyPredicate(
                    predicate_id="pred-finance-approval",
                    name="finance_approval_present",
                    description="Finance approval must be present when threshold is exceeded.",
                    predicate_type="approval",
                    operator="==",
                    expected_value=True,
                    severity="critical",
                    source_policy_id="policy-spend-threshold",
                    priority=100,
                ),
            ],
        )
        data_policy = PolicyRule(
            policy_id="policy-cross-border-data",
            name="Cross-border data transfer",
            action_types=["transfer_data"],
            decision_on_failure="BLOCKED",
            priority=200,
            description="Sensitive data transfer requires approved jurisdiction and DPO approval.",
            predicates=[
                PolicyPredicate(
                    predicate_id="pred-approved-jurisdiction",
                    name="jurisdiction_approved",
                    description="Target jurisdiction must be approved.",
                    predicate_type="membership",
                    operator="in",
                    expected_value="EU",
                    severity="critical",
                    source_policy_id="policy-cross-border-data",
                    priority=200,
                ),
                PolicyPredicate(
                    predicate_id="pred-dpo-approval",
                    name="dpo_approval_present",
                    description="DPO approval must exist for sensitive transfer.",
                    predicate_type="approval",
                    operator="==",
                    expected_value=True,
                    severity="critical",
                    source_policy_id="policy-cross-border-data",
                    priority=200,
                ),
            ],
        )
        contract_policy = PolicyRule(
            policy_id="policy-contract-amendment",
            name="Contract amendment control",
            action_types=["amend_contract"],
            decision_on_failure="REQUIRES_REVIEW",
            priority=150,
            description="Contract amendments require legal approval and active contract state.",
            predicates=[
                PolicyPredicate(
                    predicate_id="pred-contract-active",
                    name="contract_status_active",
                    description="Contract must be active.",
                    predicate_type="state",
                    operator="==",
                    expected_value="active",
                    severity="high",
                    source_policy_id="policy-contract-amendment",
                    priority=150,
                ),
                PolicyPredicate(
                    predicate_id="pred-legal-approval",
                    name="legal_approval_present",
                    description="Legal approval must be present.",
                    predicate_type="approval",
                    operator="==",
                    expected_value=True,
                    severity="high",
                    source_policy_id="policy-contract-amendment",
                    priority=150,
                ),
            ],
        )
        STORE.policies = {rule.policy_id: rule for rule in [spend_policy, data_policy, contract_policy]}

    def fetch_matching_rules(self, action_type: str) -> list[PolicyRule]:
        return sorted(
            [policy for policy in STORE.policies.values() if action_type in policy.action_types],
            key=lambda item: item.priority,
            reverse=True,
        )

    def get_policy(self, policy_id: str) -> PolicyRule | None:
        return STORE.policies.get(policy_id)


POLICY_REPOSITORY = PolicyRepository()
