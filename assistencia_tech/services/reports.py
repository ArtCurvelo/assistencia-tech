"""Serviço de relatórios operacionais e exportação CSV."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from ..data.errors import ValidationError
from ..data.repositories import DataGateway
from ..domain.clock import now_brt
from ..domain.csv_export import csv_filename, orders_csv
from ..domain.permissions import Permission, Principal, require
from ..domain.reports import (
    MonthPoint,
    OperationalReport,
    Period,
    build_report,
    default_period,
    make_period,
    monthly_series,
    orders_in_period,
)

Today = Callable[[], date]


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValidationError("Informe datas válidas para o período.") from exc


class ReportService:
    def __init__(self, gateway: DataGateway, principal: Principal | None, *, today: Today | None = None) -> None:
        self._gw = gateway
        self._principal = principal
        self._today = today or (lambda: now_brt().date())

    def default_period(self) -> Period:
        return default_period(self._today())

    def period(self, start: str | date, end: str | date) -> Period:
        return make_period(parse_date(start), parse_date(end))

    async def report(self, period: Period) -> OperationalReport:
        require(self._principal, Permission.REPORTS_VIEW)
        return build_report(await self._gw.orders.list(), await self._gw.technicians.list(), period)

    async def monthly(self) -> list[MonthPoint]:
        """Últimos 6 meses até hoje (improve-reports)."""
        require(self._principal, Permission.REPORTS_VIEW)
        return monthly_series(await self._gw.orders.list(), self._today())

    async def export_csv(self, period: Period) -> tuple[str, str]:
        """Retorna (nome do arquivo, conteúdo CSV) das ordens abertas no período."""
        require(self._principal, Permission.REPORTS_VIEW)
        orders = orders_in_period(await self._gw.orders.list(), period)
        clients = {c.id: c for c in await self._gw.clients.list()}
        equipment = {e.id: e for e in await self._gw.equipment.list()}
        technicians = {t.id: t for t in await self._gw.technicians.list()}
        return csv_filename(period.start, period.end), orders_csv(orders, clients, equipment, technicians)
