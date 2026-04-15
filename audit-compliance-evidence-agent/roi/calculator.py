from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass
class RoiInputs:
    hours_preparation_per_audit: float
    controls_per_audit: int
    evidence_items_per_audit: int
    hourly_cost_eur: float
    time_per_evidence_collection_hours: float
    time_per_review_and_followup_hours: float
    evidence_reuse_rate: float
    monthly_audits: int
    automation_reduction_preparation_rate: float
    automation_reduction_collection_rate: float
    automation_reduction_followup_rate: float
    implementation_monthly_cost_eur: float


def load_assumptions(path: Path | None = None) -> RoiInputs:
    source = path or ROOT / "assumptions.yaml"
    values: dict[str, float | int] = {}
    for raw_line in source.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = [item.strip() for item in line.split(":", 1)]
        if "." in value:
            values[key] = float(value)
        else:
            values[key] = int(value)
    return RoiInputs(**values)


def calculate_roi(inputs: RoiInputs) -> dict:
    monthly_prep_hours = inputs.hours_preparation_per_audit * inputs.monthly_audits
    monthly_collection_hours = inputs.evidence_items_per_audit * inputs.time_per_evidence_collection_hours * inputs.monthly_audits
    monthly_followup_hours = inputs.controls_per_audit * inputs.time_per_review_and_followup_hours * inputs.monthly_audits

    prep_hours_saved = monthly_prep_hours * inputs.automation_reduction_preparation_rate
    collection_hours_saved = monthly_collection_hours * inputs.automation_reduction_collection_rate
    followup_hours_saved = monthly_followup_hours * inputs.automation_reduction_followup_rate
    reuse_bonus_hours = monthly_collection_hours * inputs.evidence_reuse_rate

    total_hours_saved = prep_hours_saved + collection_hours_saved + followup_hours_saved + reuse_bonus_hours
    monthly_savings = total_hours_saved * inputs.hourly_cost_eur
    annual_savings = monthly_savings * 12
    payback_months = inputs.implementation_monthly_cost_eur / monthly_savings if monthly_savings else None

    return {
        "monthly_hours_saved": round(total_hours_saved, 2),
        "reduction_preparation_hours": round(prep_hours_saved, 2),
        "reduction_collection_hours": round(collection_hours_saved + reuse_bonus_hours, 2),
        "reduction_followup_hours": round(followup_hours_saved, 2),
        "monthly_savings_eur": round(monthly_savings, 2),
        "annual_savings_eur": round(annual_savings, 2),
        "payback_months": round(payback_months, 2) if payback_months is not None else None,
    }


def main() -> None:
    assumptions = load_assumptions()
    result = calculate_roi(assumptions)
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
