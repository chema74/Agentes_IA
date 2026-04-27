from __future__ import annotations


def build_audit_reference(level: int, summary: str) -> str:
    safe = summary.lower().replace(" ", "-")[:32]
    return f"change-l{level}-{safe}"
