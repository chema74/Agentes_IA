from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from core.db.repository import STORE
from domain.controls.models import Control
from domain.remediation.models import Remediation
from domain.scopes.models import AuditScope
from services.workflows.audit_workflow import WORKFLOW


ROOT = Path(__file__).resolve().parents[1]


def reset_store() -> None:
    STORE.scopes.clear()
    STORE.controls.clear()
    STORE.evidence.clear()
    STORE.mappings.clear()
    STORE.coverage.clear()
    STORE.gaps.clear()
    STORE.findings.clear()
    STORE.remediations.clear()
    STORE.packages.clear()


def seed_demo_data(reset: bool = False) -> None:
    if reset:
        reset_store()

    scope = AuditScope(
        id="ISO27001-demo",
        name="ISO27001-demo",
        description="Revision demo de controles operativos y evidencias para preparacion de auditoria.",
        framework="ISO 27001",
        status="in_review",
        created_by="demo-compliance",
    )
    WORKFLOW.create_scope(scope)

    controls = [
        Control(id="control-access-001", scope_id=scope.id, code="A.5.15", name="Revision periodica de accesos privilegiados", description="Los accesos privilegiados deben revisarse de forma periodica y con trazabilidad.", category="access_management", criticality="high", expected_criterion="Debe existir procedimiento, evidencia de revision y owner asignado.", status="active", owner_user_id="demo-owner"),
        Control(id="control-logging-002", scope_id=scope.id, code="A.8.15", name="Monitorizacion y conservacion de logs", description="Los logs operativos deben conservarse y revisarse para detectar anomalias.", category="logging", criticality="medium", expected_criterion="Deben existir logs, criterios de conservacion y seguimiento.", status="active"),
        Control(id="control-ticketing-003", scope_id=scope.id, code="OPS-12", name="Seguimiento de incidencias criticas", description="Las incidencias criticas deben tener ticket, owner y remediacion.", category="incident_management", criticality="critical", expected_criterion="Debe haber tickets exportados y remediaciones trazables.", status="active", owner_user_id="demo-owner"),
    ]
    for control in controls:
        WORKFLOW.create_control(control, actor_user_id="demo-compliance")

    evidence_files = [
        ("sample_data/evidence/policy_access_review.txt", "manual_upload"),
        ("sample_data/logs/auth_review_log.txt", "log_export"),
        ("sample_data/tickets/security_tickets.csv", "ticket_export"),
        ("sample_data/evidence/network_diagram.png", "manual_upload"),
    ]
    for relative_path, source_type in evidence_files:
        path = ROOT / relative_path
        WORKFLOW.ingest_evidence(scope_id=scope.id, filename=path.name, content=path.read_bytes(), uploaded_by="demo-owner", source_type=source_type, source_name=path.name)

    suggested = WORKFLOW.suggest_mappings_for_scope(scope.id)
    for mapping in suggested:
        WORKFLOW.review_mapping(mapping.id, reviewed_by="demo-auditor", approved=mapping.confidence >= 0.5)

    result = WORKFLOW.evaluate_scope(scope.id)
    if result["findings"]:
        remediation = Remediation(id=f"rem-{uuid4().hex[:10]}", scope_id=scope.id, finding_id=result["findings"][0].id, title="Definir owner y reforzar evidencia del control", description="Asignar owner formal y adjuntar evidencia adicional antes de cierre.", status="in_progress", owner_user_id="demo-owner")
        WORKFLOW.create_remediation(remediation, actor_user_id="demo-compliance")


if __name__ == "__main__":
    seed_demo_data(reset=True)
    print("Dataset demo cargado.")
