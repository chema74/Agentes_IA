from __future__ import annotations

from scripts.seed_mock_data import reset_store


def test_redaction_masks_email_and_phone():
    from core.security.redaction import redact_text

    text = "Contacto: user@example.com y +34 600 123 123"
    redacted = redact_text(text)
    assert "user@example.com" not in redacted
    assert "+34 600 123 123" not in redacted
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted


def test_roi_calculation_returns_positive_savings():
    from roi.calculator import calculate_roi, load_assumptions

    result = calculate_roi(load_assumptions())
    assert result["monthly_savings_eur"] > 0
    assert result["annual_savings_eur"] >= result["monthly_savings_eur"]


def test_seed_demo_data_populates_store():
    from core.db.repository import STORE
    from scripts.seed_mock_data import seed_demo_data

    reset_store()
    seed_demo_data(reset=False)
    assert STORE.scopes
    assert STORE.controls
    assert STORE.evidence
