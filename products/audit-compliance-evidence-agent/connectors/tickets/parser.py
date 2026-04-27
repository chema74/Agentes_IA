from __future__ import annotations

import csv
from io import StringIO


def parse_ticket_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(text))
    return [dict(row) for row in reader]
