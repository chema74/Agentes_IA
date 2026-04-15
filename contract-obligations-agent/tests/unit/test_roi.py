from __future__ import annotations

from pathlib import Path

from roi.calculator import calculate_roi, roi_summary


def test_roi_calculator_returns_breakdown(tmp_path: Path) -> None:
    assumptions = tmp_path / "assumptions.yaml"
    assumptions.write_text(
        "\n".join(
            [
                "hours_per_contract_manual_review: 2",
                "contracts_per_month: 10",
                "cost_per_hour: 50",
                "hours_saved_initial_extraction: 0.5",
                "hours_saved_followup_tracking: 0.25",
                "omission_reduction_rate: 0.1",
                "monthly_admin_error_cost: 1000",
            ]
        ),
        encoding="utf-8",
    )

    result = calculate_roi(assumptions)
    assert result.manual_review_cost_monthly == 1000
    assert result.extraction_savings_monthly == 250
    assert result.tracking_savings_monthly == 125
    assert result.omission_savings_monthly == 100
    assert result.total_monthly_savings == 475
    assert result.annual_savings == 5700
    assert result.payback_months > 0


def test_roi_summary_is_json_ready(tmp_path: Path) -> None:
    assumptions = tmp_path / "assumptions.yaml"
    assumptions.write_text("contracts_per_month: 1\n", encoding="utf-8")
    result = roi_summary(assumptions)
    assert "total_monthly_savings" in result
    assert "payback_months" in result
