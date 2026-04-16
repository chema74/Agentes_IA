from __future__ import annotations

import json

import httpx

from domain.cases.models import ChangeCase, Recommendation
from domain.friction.models import FrictionAssessment
from domain.interventions.models import InterventionPlan
from domain.progress.models import ChangeFatigueAlert, HumanSupervisionGate
from domain.resistance.models import ResistanceProfile
from services.storage.neon_vector_store import NeonPgVectorStore
from services.storage.supabase_adapter import SupabaseStore
from services.storage.upstash_adapter import UpstashRedisCache


def _sample_case() -> ChangeCase:
    return ChangeCase(
        case_id="case-ext",
        estado_del_proceso_de_cambio="observation",
        perfil_de_resistencia=ResistanceProfile(resistance_type="legitimate_concern", intensity="low", rationale="test"),
        nivel_de_friccion=FrictionAssessment(level="low", confidence=0.9, process_status="en_observacion"),
        plan_de_intervencion=InterventionPlan(focus="monitor", steps=[]),
        alerta_de_fatiga_de_cambio=ChangeFatigueAlert(level="low", evidence="none"),
        revision_humana_requerida=False,
        estado_de_la_puerta_de_supervision_humana=HumanSupervisionGate(status="monitoring", owner="lider", rationale="ok"),
        recomendacion_final=Recommendation(summary="seguir", level=1, rationale="ok"),
        referencia_de_auditoria="audit-ext",
    )


class _FakeResponse:
    def __init__(self, status_code: int = 200, payload=None) -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else []
        self.request = httpx.Request("GET", "https://example.test")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=self.request, response=httpx.Response(self.status_code, request=self.request))

    def json(self):
        return self._payload


class _FakeClient:
    responses: list[_FakeResponse] = []
    calls: list[dict] = []

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, headers=None, params=None, json=None, content=None):
        self.calls.append({"method": "POST", "url": url, "headers": headers, "params": params, "json": json, "content": content})
        return self.responses.pop(0)

    def get(self, url, headers=None, params=None):
        self.calls.append({"method": "GET", "url": url, "headers": headers, "params": params})
        return self.responses.pop(0)


def test_supabase_store_retries_once_and_sends_expected_payload(monkeypatch):
    store = SupabaseStore()
    monkeypatch.setattr(httpx, "Client", _FakeClient)
    _FakeClient.calls = []
    _FakeClient.responses = [_FakeResponse(status_code=500), _FakeResponse(status_code=200)]
    monkeypatch.setattr(store, "_base_url", "https://supabase.test")
    monkeypatch.setattr(store, "_retry_delay", 0)
    case = _sample_case()
    store.save_case(case)
    assert len(_FakeClient.calls) == 2
    payload = _FakeClient.calls[-1]["json"]
    assert payload["case_id"] == case.case_id
    assert payload["audit_reference"] == case.referencia_de_auditoria


def test_upstash_cache_round_trips_json(monkeypatch):
    cache = UpstashRedisCache()
    monkeypatch.setattr(httpx, "Client", _FakeClient)
    _FakeClient.calls = []
    _FakeClient.responses = [
        _FakeResponse(status_code=200, payload={"result": "OK"}),
        _FakeResponse(status_code=200, payload={"result": json.dumps({"value": 1})}),
    ]
    monkeypatch.setattr(cache, "_base_url", "https://upstash.test")
    monkeypatch.setattr(cache, "_retry_delay", 0)
    cache.set_json("key-1", {"value": 1})
    loaded = cache.get_json("key-1")
    assert loaded == {"value": 1}
    assert _FakeClient.calls[0]["content"] == json.dumps(["SET", "key-1", json.dumps({"value": 1}, ensure_ascii=True)])


def test_neon_vector_store_indexes_case_with_pgvector_sql(monkeypatch):
    store = NeonPgVectorStore()
    executed: list[tuple[str, tuple | None]] = []

    class _Cursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, sql, params=None):
            executed.append((sql, params))

        def fetchone(self):
            return (1,)

    class _Connection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def cursor(self):
            return _Cursor()

        def commit(self):
            return None

    class _PsycopgModule:
        def connect(self, dsn):
            return _Connection()

    monkeypatch.setattr("services.storage.neon_vector_store.psycopg", _PsycopgModule())
    monkeypatch.setattr(store, "_dsn", "postgresql://neon.test/db")
    monkeypatch.setattr(store, "_dimensions", 4)
    store.index_case(_sample_case())
    assert any("CREATE EXTENSION IF NOT EXISTS vector" in sql for sql, _ in executed)
    insert_calls = [item for item in executed if "INSERT INTO change_case_vectors" in item[0]]
    assert insert_calls
    assert insert_calls[-1][1][0] == "case-ext"
