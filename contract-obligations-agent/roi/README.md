# ROI

Editable assumptions live in `assumptions.yaml`.

The calculator is intentionally transparent:

- hours per contract review
- contracts per month
- cost per hour
- extraction savings
- follow-up tracking savings
- omission reduction estimate
- monthly and annual savings
- payback estimate

The calculator exposes a breakdown so assumptions can be audited:

- manual review cost baseline
- extraction savings
- follow-up tracking savings
- omission savings
- total monthly savings
- annual savings
- payback in months

Use `python -m roi.calculator` from the project root to print the current ROI breakdown as JSON.
