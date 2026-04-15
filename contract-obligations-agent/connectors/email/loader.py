from __future__ import annotations

from email import policy
from email.parser import BytesParser


def parse_eml(content: bytes) -> dict[str, str]:
    msg = BytesParser(policy=policy.default).parsebytes(content)
    body = msg.get_body(preferencelist=("plain",))
    return {
        "subject": msg.get("subject", ""),
        "from": msg.get("from", ""),
        "to": msg.get("to", ""),
        "date": msg.get("date", ""),
        "body": body.get_content() if body else msg.get_content(),
    }

