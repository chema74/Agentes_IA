from __future__ import annotations

from domain.routes.models import RouteDisruptionAlert
from domain.signals.models import GeopoliticalSignal


def map_route_risk(route: str | None, signals: list[GeopoliticalSignal]) -> list[RouteDisruptionAlert]:
    if route is None:
        return []
    alerts: list[RouteDisruptionAlert] = []
    for signal in signals:
        if signal.category == "route":
            alerts.append(RouteDisruptionAlert(route=route, severity="critical" if signal.intensity == "critical" else "high", description=signal.summary))
    return alerts
