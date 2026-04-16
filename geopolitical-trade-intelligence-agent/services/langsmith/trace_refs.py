from __future__ import annotations


def build_audit_reference(level: int, country: str) -> str:
    safe = country.lower().replace(" ", "-")[:24]
    return f"trade-l{level}-{safe}"
