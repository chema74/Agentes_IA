from __future__ import annotations

import httpx

from core.config.settings import settings
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
        if not settings.enable_fallback_policy_store and settings.supabase_url and settings.supabase_service_role_key:
            remote = self._fetch_remote_rules(action_type)
            if remote:
                return remote
        return sorted(
            [policy for policy in STORE.policies.values() if action_type in policy.action_types],
            key=lambda item: item.priority,
            reverse=True,
        )

    def get_policy(self, policy_id: str) -> PolicyRule | None:
        if not settings.enable_fallback_policy_store and settings.supabase_url and settings.supabase_service_role_key:
            remote = self._fetch_remote_policy(policy_id)
            if remote is not None:
                return remote
        return STORE.policies.get(policy_id)

    def health(self) -> dict:
        if settings.enable_fallback_policy_store or not settings.supabase_url or not settings.supabase_service_role_key:
            return {"status": "fallback", "backend": "in-memory"}
        try:
            with httpx.Client(timeout=settings.intent_typing_timeout_seconds, headers=self._headers()) as client:
                response = client.get(f"{settings.supabase_url}/rest/v1/policies", params={"limit": "1"})
                response.raise_for_status()
            return {"status": "ok", "backend": "supabase"}
        except Exception as exc:
            return {"status": "error", "backend": "supabase", "detail": str(exc)}

    def _fetch_remote_rules(self, action_type: str) -> list[PolicyRule]:
        try:
            with httpx.Client(timeout=settings.intent_typing_timeout_seconds, headers=self._headers()) as client:
                response = client.get(f"{settings.supabase_url}/rest/v1/policies", params={"action_type": f"cs.{{{action_type}}}"})
                response.raise_for_status()
            return [PolicyRule.model_validate(item) for item in response.json()]
        except Exception:
            return []

    def _fetch_remote_policy(self, policy_id: str) -> PolicyRule | None:
        try:
            with httpx.Client(timeout=settings.intent_typing_timeout_seconds, headers=self._headers()) as client:
                response = client.get(f"{settings.supabase_url}/rest/v1/policies", params={"policy_id": f"eq.{policy_id}", "limit": "1"})
                response.raise_for_status()
            data = response.json()
            if not data:
                return None
            return PolicyRule.model_validate(data[0])
        except Exception:
            return None

    def _headers(self) -> dict:
        return {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
        }


POLICY_REPOSITORY = PolicyRepository()
