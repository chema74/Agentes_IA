from __future__ import annotations

from domain.audit.models import AuditEvent
from domain.cases.models import ChangeCase, Recommendation
from domain.friction.models import FrictionAssessment
from domain.interventions.models import InterventionPlan
from domain.progress.models import ChangeFatigueAlert, HumanSupervisionGate
from domain.resistance.models import ResistanceProfile
from services.storage.repositories import StorageRuntime


class _StubCaseStore:
    mode = "stub-case"

    def __init__(self) -> None:
        self.case = None
        self.events = []

    def save_case(self, item):
        self.case = item

    def get_case(self, case_id: str):
        return self.case if self.case and self.case.case_id == case_id else None

    def append_audit_event(self, event):
        self.events.append(event)

    def audit_events_by_reference(self, reference: str):
        return [event for event in self.events if event.reference == reference]

    def health(self):
        return {"status": "ok", "backend": self.mode}


class _FailingCache:
    mode = "failing-cache"

    def set_json(self, key: str, value: dict) -> None:
        raise RuntimeError("cache unavailable")

    def get_json(self, key: str):
        return None

    def health(self):
        return {"status": "error", "backend": self.mode}


class _FailingVector:
    mode = "failing-vector"

    def index_case(self, item) -> None:
        raise RuntimeError("vector unavailable")

    def health(self):
        return {"status": "error", "backend": self.mode}


def _sample_case() -> ChangeCase:
    return ChangeCase(
        case_id="case-1",
        estado_del_proceso_de_cambio="observation",
        perfil_de_resistencia=ResistanceProfile(resistance_type="legitimate_concern", intensity="low", rationale="test"),
        nivel_de_friccion=FrictionAssessment(level="low", confidence=0.9, process_status="en_observacion"),
        plan_de_intervencion=InterventionPlan(focus="monitor", steps=[]),
        alerta_de_fatiga_de_cambio=ChangeFatigueAlert(level="low", evidence="none"),
        revision_humana_requerida=False,
        estado_de_la_puerta_de_supervision_humana=HumanSupervisionGate(status="monitoring", owner="lider", rationale="ok"),
        recomendacion_final=Recommendation(summary="seguir", level=1, rationale="ok"),
        referencia_de_auditoria="audit-1",
    )


def test_storage_runtime_keeps_primary_store_when_cache_and_vector_fail():
    runtime = StorageRuntime(_StubCaseStore(), _FailingCache(), _FailingVector())
    case = _sample_case()
    runtime.save_case(case)
    loaded = runtime.get_case(case.case_id)
    assert loaded is not None
    assert loaded.case_id == case.case_id


def test_storage_runtime_appends_audit_events_to_primary_store():
    runtime = StorageRuntime(_StubCaseStore(), _FailingCache(), _FailingVector())
    event = AuditEvent(id="evt-1", reference="audit-1", entity_type="CHANGE_CASE", entity_id="case-1", action="evaluated", payload={"ok": True})
    runtime.append_audit_event(event)
    assert runtime.audit_events_by_reference("audit-1")
