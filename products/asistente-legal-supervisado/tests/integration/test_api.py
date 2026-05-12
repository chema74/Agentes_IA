from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


def _headers() -> dict:
    return {"X-API-Key": "legal-dev-key"}


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_review_contract_returns_required_contract():
    from app.main import app

    client = TestClient(app)
    text = """
    Master Services Agreement
    Supplier shall have unlimited liability for all losses.
    Governing law: Delaware exclusive.
    Data may be transferred outside EU without restriction.
    """
    response = client.post("/api/contracts/review", json={"contract_text": text, "counterparty_name": "VendorCo"}, headers=_headers())
    body = response.json()
    assert response.status_code == 200
    for key in [
        "contract_type",
        "clause_map",
        "risk_clauses",
        "redline_suggestions",
        "negotiation_status",
        "approval_recommendation",
        "human_review_required",
        "legal_notes",
        "audit_reference",
    ]:
        assert key in body


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_blocked_contract_with_prohibited_clauses():
    from app.main import app

    client = TestClient(app)
    text = """
    Master Services Agreement
    Supplier shall have unlimited liability for all losses.
    Governing law: Delaware exclusive.
    """
    response = client.post("/api/contracts/review", json={"contract_text": text, "counterparty_name": "VendorCo"}, headers=_headers())
    assert response.status_code == 200
    assert response.json()["approval_recommendation"]["status"] == "BLOCKED"


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_negotiable_contract_with_redlines():
    from app.main import app

    client = TestClient(app)
    text = """
    Master Services Agreement
    Either party may terminate for convenience.
    """
    response = client.post("/api/contracts/redline", json={"contract_text": text, "counterparty_name": "VendorCo"}, headers=_headers())
    assert response.status_code == 200
    assert response.json()["approval_recommendation"]["status"] in {"NEGOTIABLE", "APPROVABLE"}


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_negotiate_persists_track_and_audit():
    from app.main import app

    client = TestClient(app)
    text = """
    Master Services Agreement
    Supplier shall have unlimited liability for all losses.
    """
    response = client.post(
        "/api/contracts/negotiate",
        json={"contract_text": text, "counterparty_name": "VendorCo", "issue_key": "liability", "counterparty_response": "We can cap liability."},
        headers=_headers(),
    )
    body = response.json()
    review = client.get(f"/api/reviews/{body['review_id']}", headers=_headers())
    audit = client.get(f"/api/audit/{body['audit_reference']}", headers=_headers())
    assert response.status_code == 200
    assert review.status_code == 200
    assert audit.status_code == 200
    assert review.json()["negotiation_tracks"]


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_api_requires_key():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/contracts/review", json={"contract_text": "NDA", "counterparty_name": "VendorCo"})
    assert response.status_code == 401
