from __future__ import annotations

import json

from domain.audit.models import AuditEvent
from domain.cases.models import ChangeCase, Recommendation
from domain.friction.models import FrictionAssessment
from domain.interventions.models import InterventionPlan
from domain.progress.models import ChangeFatigueAlert, HumanSupervisionGate
from domain.resistance.models import ResistanceProfile
from services.storage.repositories import STORE


def build_smoke_case() -> ChangeCase:
    return ChangeCase(
        case_id="smoke-case",
        estado_del_proceso_de_cambio="observation",
        perfil_de_resistencia=ResistanceProfile(resistance_type="legitimate_concern", intensity="low", rationale="smoke"),
        nivel_de_friccion=FrictionAssessment(level="low", confidence=0.95, process_status="en_observacion"),
        plan_de_intervencion=InterventionPlan(focus="smoke", steps=[]),
        alerta_de_fatiga_de_cambio=ChangeFatigueAlert(level="low", evidence="none"),
        revision_humana_requerida=False,
        estado_de_la_puerta_de_supervision_humana=HumanSupervisionGate(status="monitoring", owner="system", rationale="smoke"),
        recomendacion_final=Recommendation(summary="ok", level=1, rationale="smoke"),
        referencia_de_auditoria="smoke-audit",
    )


def main() -> None:
    report = {"health": STORE.health_report()}
    case = build_smoke_case()
    STORE.save_case(case)
    loaded = STORE.get_case(case.case_id)
    event = AuditEvent(
        id="smoke-event",
        reference=case.referencia_de_auditoria,
        entity_type="CHANGE_CASE",
        entity_id=case.case_id,
        action="smoke_checked",
        payload={"status": "ok"},
    )
    STORE.append_audit_event(event)
    audit_events = STORE.audit_events_by_reference(case.referencia_de_auditoria)
    report["roundtrip"] = {
        "case_saved": loaded is not None,
        "case_id": loaded.case_id if loaded else None,
        "audit_events": len(audit_events),
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
