from __future__ import annotations

from zipfile import ZipFile

from scripts.seed_mock_data import reset_store


def test_seed_and_export_package(tmp_path):
    from core.db.repository import STORE
    from scripts.seed_mock_data import seed_demo_data
    from services.workflows.audit_workflow import WORKFLOW

    reset_store()
    seed_demo_data(reset=False)
    package = WORKFLOW.export_package("ISO27001-demo", created_by="demo-auditor")
    assert package.storage_path
    stored = WORKFLOW.storage.adapter.read(package.storage_path)
    zip_path = tmp_path / "package.zip"
    zip_path.write_bytes(stored)
    with ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "cover.md" in names
    assert "controls.csv" in names
    assert "audit_package.docx" in names
    assert STORE.packages


def test_ingest_evidence_persists_metadata():
    from services.workflows.audit_workflow import WORKFLOW
    from domain.scopes.models import AuditScope

    reset_store()
    WORKFLOW.create_scope(AuditScope(id="scope-test", name="Scope test", created_by="demo-compliance"))
    evidence = WORKFLOW.ingest_evidence("scope-test", "note.txt", b"politica de accesos\ncontacto: user@example.com", "demo-owner")
    assert evidence.id.startswith("evidence-")
    assert evidence.classification in {"policy", "text"}
    assert evidence.storage_path
    assert evidence.content_hash
