from __future__ import annotations

import re


INFO_RE = re.compile(r"\bINFO\b", re.IGNORECASE)
WARNING_RE = re.compile(r"\bWARN(?:ING)?\b", re.IGNORECASE)
ERROR_RE = re.compile(r"\bERROR\b", re.IGNORECASE)


def parse_log_lines(text: str) -> dict[str, int | bool]:
    lines = [line for line in text.splitlines() if line.strip()]
    info_count = sum(1 for line in lines if INFO_RE.search(line))
    warning_count = sum(1 for line in lines if WARNING_RE.search(line))
    error_count = sum(1 for line in lines if ERROR_RE.search(line))
    return {
        "line_count": len(lines),
        "info_count": info_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "has_errors": error_count > 0,
    }
