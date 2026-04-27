from __future__ import annotations

from core.security.redaction import redact_sensitive_text


def test_redaction_masks_contact_and_account_data() -> None:
    text = "Contact legal@example.com or +34 600 123 456. IBAN ES12ABC1234567890123 and ID 12345678Z."
    redacted = redact_sensitive_text(text)
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted
    assert "[redacted-iban]" in redacted
    assert "[redacted-id]" in redacted
