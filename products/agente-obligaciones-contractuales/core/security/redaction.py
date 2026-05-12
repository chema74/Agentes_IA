from __future__ import annotations

import re


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<![A-Z0-9])\+?\d[\d\s().-]{7,}\d(?![A-Z0-9])")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.I)
SPANISH_ID_RE = re.compile(r"\b\d{8}[A-Z]\b")
LONG_ACCOUNT_RE = re.compile(r"\b\d{10,20}\b")


def redact_sensitive_text(text: str) -> str:
    text = EMAIL_RE.sub("[redacted-email]", text)
    text = IBAN_RE.sub("[redacted-iban]", text)
    text = SPANISH_ID_RE.sub("[redacted-id]", text)
    text = LONG_ACCOUNT_RE.sub("[redacted-account]", text)
    text = PHONE_RE.sub("[redacted-phone]", text)
    return text
