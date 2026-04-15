from __future__ import annotations

from core.db.repository import STORE


def dashboard_metrics() -> dict:
    open_findings = [item for item in STORE.findings.values() if item.status != "closed"]
    pending_remediations = [item for item in STORE.remediations.values() if item.status not in {"done", "closed"}]
    unresolved_gaps = [item for item in STORE.gaps.values() if item.status != "resolved"]
    return {
        "scope_count": len(STORE.scopes),
        "control_count": len(STORE.controls),
        "evidence_count": len(STORE.evidence),
        "open_findings": len(open_findings),
        "pending_remediations": len(pending_remediations),
        "unresolved_gaps": len(unresolved_gaps),
    }


def scopes_with_stats() -> list[dict]:
    results = []
    for scope in STORE.scopes.values():
        controls = [item for item in STORE.controls.values() if item.scope_id == scope.id]
        evidence_items = [item for item in STORE.evidence.values() if item.scope_id == scope.id]
        findings = [item for item in STORE.findings.values() if item.scope_id == scope.id]
        results.append({"scope": scope, "controls": len(controls), "evidence": len(evidence_items), "findings": len(findings)})
    return results
