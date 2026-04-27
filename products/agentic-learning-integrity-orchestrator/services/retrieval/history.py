from __future__ import annotations

from domain.evidence.models import EvidenceTrace


def summarize_history(traces: list[EvidenceTrace]) -> str:
    if not traces:
        return ""
    recent = traces[-3:]
    return " | ".join(trace.process_summary for trace in recent)
