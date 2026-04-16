from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


def _payload(authorized_incremental_cost: float = 300, regulatory_constraints: list[str] | None = None) -> dict:
    now = datetime.now(UTC)
    return {
        "task": {
            "id": "task-api-1",
            "shipment_reference": "SHIP-API-1",
            "order_reference": "ORD-API-1",
            "origin": "Madrid",
            "destination": "Barcelona",
            "committed_pickup_at": now.isoformat(),
            "committed_delivery_at": (now + timedelta(hours=8)).isoformat(),
            "mode": "road",
            "capacity_required": 10,
            "capacity_unit": "pallet",
            "base_cost": 1000,
            "currency": "EUR",
            "priority": "critical",
            "sla_target_minutes": 240,
            "authorized_incremental_cost": authorized_incremental_cost,
            "operational_constraints": [],
            "regulatory_constraints": regulatory_constraints or [],
            "service_tier": "standard",
            "current_status": "delayed"
        },
        "disruption": {
            "id": "dis-api-1",
            "task_id": "task-api-1",
            "disruption_type": "port_congestion",
            "severity": "high",
            "summary": "Port feeder missed slot",
            "estimated_delay_minutes": 220,
            "affected_capacity_delta": 10
        }
    }


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_evaluate_returns_required_contract():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/disruptions/evaluate", json=_payload())
    assert response.status_code == 200
    body = response.json()
    for key in [
        "disruption_status",
        "affected_tasks",
        "peer_discovery_summary",
        "negotiation_results",
        "sla_risk",
        "selected_recovery_plan",
        "execution_status",
        "human_review_required",
        "justification",
        "audit_reference",
    ]:
        assert key in body


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_disruption_with_verified_peers_generates_plan():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/disruptions/evaluate", json=_payload())
    body = response.json()
    assert response.status_code == 200
    assert body["peer_discovery_summary"]["viable_peer_count"] >= 1
    assert body["selected_recovery_plan"]["plan_id"]


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_cost_overrun_blocks_execution():
    from app.main import app

    client = TestClient(app)
    payload = _payload(authorized_incremental_cost=20)
    response = client.post("/api/recovery/execute", json=payload)
    body = response.json()
    assert response.status_code == 200
    assert body["execution_status"] == "blocked"
    assert body["selected_recovery_plan"]["status"] == "BLOCKED"


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_regulatory_mismatch_keeps_human_review():
    from app.main import app

    client = TestClient(app)
    payload = _payload(regulatory_constraints=["GDP", "Temperature-Controlled"])
    response = client.post("/api/disruptions/evaluate", json=payload)
    body = response.json()
    assert response.status_code == 200
    assert body["selected_recovery_plan"]["status"] in {"BLOCKED", "PENDING_REVIEW"}


@pytest.mark.skipif(TestClient is None, reason="FastAPI no instalado en el entorno actual.")
def test_execute_persists_audit_reference():
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/recovery/execute", json=_payload(authorized_incremental_cost=400))
    body = response.json()
    audit = client.get(f"/api/audit/{body['audit_reference']}")
    assert response.status_code == 200
    assert audit.status_code == 200
    assert len(audit.json()["events"]) >= 3
