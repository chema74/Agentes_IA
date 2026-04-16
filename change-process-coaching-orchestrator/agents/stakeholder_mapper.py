from __future__ import annotations

from domain.stakeholders.models import StakeholderEntry


def map_stakeholders(context_type: str) -> list[StakeholderEntry]:
    if context_type == "individual":
        return [StakeholderEntry(actor="persona", influence="high", alignment="mixed", support_needed="reflection and sequencing")]
    return [
        StakeholderEntry(actor="lider", influence="high", alignment="partial", support_needed="decision clarity"),
        StakeholderEntry(actor="equipo", influence="high", alignment="mixed", support_needed="capacity and communication"),
    ]
