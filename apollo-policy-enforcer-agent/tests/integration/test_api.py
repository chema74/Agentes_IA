from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


def _payload(request_text: str, context: dict) -> dict:
    return {
        "request_text": request_text,
        "actor_id": "user-api-1",
        "target_resource": "resource-1",
        "context": context,
    }


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_enforce_returns_required_contract():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/enforce", json=_payload("Please approve spend for this invoice", {"amount": 2000, "currency": "EUR", "finance_approval_present": True}))
    body = response.json()
    assert response.status_code == 200
    for key in [
        "typed_intent",
        "matched_predicates",
        "symbolic_state",
        "validation_trace",
        "conflicts_detected",
        "action_mandate",
        "explanation",
        "audit_reference",
    ]:
        assert key in body


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_authorized_spend_when_predicates_hold():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/enforce", json=_payload("Please approve spend for this invoice", {"amount": 2000, "currency": "EUR", "finance_approval_present": True}))
    assert response.status_code == 200
    assert response.json()["action_mandate"]["decision"] == "AUTHORIZED"


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_blocks_cross_border_transfer_without_dpo_approval():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/enforce", json=_payload("Transfer customer data to a processor", {"jurisdiction": "EU", "data_domain": "customer", "dpo_approval_present": False}))
    assert response.status_code == 200
    assert response.json()["action_mandate"]["decision"] in {"BLOCKED", "REQUIRES_REVIEW"}


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_validate_does_not_persist_mandate_but_audits():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/validate", json=_payload("Amend the contract with supplier", {"contract_status": "active", "legal_approval_present": True}))
    body = response.json()
    mandate_id = body["action_mandate"]["mandate_id"]
    missing = client.get(f"/api/mandates/{mandate_id}")
    audit = client.get(f"/api/audit/{body['audit_reference']}")
    assert response.status_code == 200
    assert missing.status_code == 404
    assert audit.status_code == 200


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_policy_lookup_works():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/policies/policy-cross-border-data")
    assert response.status_code == 200
    assert response.json()["policy_id"] == "policy-cross-border-data"
