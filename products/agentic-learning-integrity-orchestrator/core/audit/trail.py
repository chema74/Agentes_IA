from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4


def make_audit_reference(prefix: str = "AUD") -> str:
    return f"{prefix}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
