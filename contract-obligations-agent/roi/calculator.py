from __future__ import annotations

from dataclasses import dataclass
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
class ROIResult:
    monthly_savings: float
    annual_savings: float
    payback_months: float


def calculate_roi(assumptions_path: str | Path) -> ROIResult:
    assumptions = _parse_simple_yaml(Path(assumptions_path))
    monthly = assumptions["contracts_per_month"] * (
        assumptions["hours_saved_initial_extraction"] + assumptions["hours_saved_followup_tracking"]
    ) * assumptions["cost_per_hour"]
    monthly += assumptions["monthly_admin_error_cost"] * assumptions["omission_reduction_rate"]
    annual = monthly * 12
    investment = assumptions["hours_per_contract_manual_review"] * assumptions["contracts_per_month"] * assumptions["cost_per_hour"]
    payback = investment / monthly if monthly else 0.0
    return ROIResult(monthly_savings=monthly, annual_savings=annual, payback_months=payback)


if __name__ == "__main__":
    result = calculate_roi(Path(__file__).with_name("assumptions.yaml"))
    print(json.dumps(result.__dict__, indent=2))

