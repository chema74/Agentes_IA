from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


DEFAULTS = {
    "hours_per_contract_manual_review": 1.5,
    "contracts_per_month": 120,
    "cost_per_hour": 45,
    "hours_saved_initial_extraction": 0.35,
    "hours_saved_followup_tracking": 0.20,
    "omission_reduction_rate": 0.15,
    "monthly_admin_error_cost": 800,
}


def _parse_simple_yaml(path: Path) -> dict:
    if not path.exists():
        return dict(DEFAULTS)
    data: dict[str, float] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        try:
            data[key.strip()] = float(value.strip())
        except ValueError:
            continue
    return {**DEFAULTS, **data}


@dataclass
class ROIBreakdown:
    manual_review_cost_monthly: float
    extraction_savings_monthly: float
    tracking_savings_monthly: float
    omission_savings_monthly: float
    total_monthly_savings: float
    annual_savings: float
    payback_months: float


def calculate_roi(assumptions_path: str | Path) -> ROIBreakdown:
    assumptions = _parse_simple_yaml(Path(assumptions_path))
    manual_review_cost = assumptions["hours_per_contract_manual_review"] * assumptions["contracts_per_month"] * assumptions["cost_per_hour"]
    extraction_savings = assumptions["contracts_per_month"] * assumptions["hours_saved_initial_extraction"] * assumptions["cost_per_hour"]
    tracking_savings = assumptions["contracts_per_month"] * assumptions["hours_saved_followup_tracking"] * assumptions["cost_per_hour"]
    omission_savings = assumptions["monthly_admin_error_cost"] * assumptions["omission_reduction_rate"]
    total_monthly_savings = extraction_savings + tracking_savings + omission_savings
    annual_savings = total_monthly_savings * 12
    payback_months = manual_review_cost / total_monthly_savings if total_monthly_savings else 0.0
    return ROIBreakdown(
        manual_review_cost_monthly=manual_review_cost,
        extraction_savings_monthly=extraction_savings,
        tracking_savings_monthly=tracking_savings,
        omission_savings_monthly=omission_savings,
        total_monthly_savings=total_monthly_savings,
        annual_savings=annual_savings,
        payback_months=payback_months,
    )


def roi_summary(assumptions_path: str | Path) -> dict:
    result = calculate_roi(assumptions_path)
    return asdict(result)


if __name__ == "__main__":
    result = roi_summary(Path(__file__).with_name("assumptions.yaml"))
    print(json.dumps(result, indent=2, ensure_ascii=False))
