from __future__ import annotations

from pydantic import BaseModel


class RouteDisruptionAlert(BaseModel):
    route: str
    severity: str
    description: str
