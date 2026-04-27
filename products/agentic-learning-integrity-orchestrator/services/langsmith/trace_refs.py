from __future__ import annotations

from core.audit.trail import make_audit_reference


def build_audit_payload(level: int, recommendation: str) -> str:
    return f"{make_audit_reference('LEARN')}-{level}-{recommendation}"
