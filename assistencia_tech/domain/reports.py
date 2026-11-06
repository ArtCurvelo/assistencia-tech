"""Relatórios operacionais por período (funções puras)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from ..data.errors import ValidationError
from ..models import PAYMENT_METHODS, OrderStatus, ServiceOrder, Technician
from .clock import BRT
from .pricing import compute_totals
from .validators import quantize

DEFAULT_PERIOD_DAYS = 90
FINISHED = frozenset({OrderStatus.DONE, OrderStatus.DELIVERED})
ZERO = Decimal("0.00")


@dataclass(frozen=True)
class Period:
    start: date
    end: date

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment.astimezone(BRT).date() <= self.end


def make_period(start: date, end: date) -> Period:
    if start > end:
        raise ValidationError("Período inválido: a data inicial é posterior à data final.")
    return Period(start, end)


def default_period(today: date) -> Period:
    return Period(today - timedelta(days=DEFAULT_PERIOD_DAYS), today)


@dataclass(frozen=True)
class VolumeReport:
    opened: int
    delivered: int
    cancelled: int
    in_progress: int


@dataclass(frozen=True)
class RevenueReport:
    total: Decimal
    by_method: dict[str, Decimal]
    delivered_count: int
    average_ticket: Decimal | None


@dataclass(frozen=True)
class TechnicianRow:
    name: str
    assigned: int
    finished: int
    budget_total: Decimal


@dataclass(frozen=True)
class TurnaroundReport:
    average_days: float | None
    count: int


@dataclass(frozen=True)
class OperationalReport:
    period: Period
    volume: VolumeReport
    revenue: RevenueReport
    technicians: tuple[TechnicianRow, ...]
    turnaround: TurnaroundReport


def _first_status_event(order: ServiceOrder, status: OrderStatus) -> datetime | None:
    return next((e.at for e in order.history if e.to_status == status.value), None)


def volume(orders: list[ServiceOrder]) -> VolumeReport:
    delivered = sum(1 for o in orders if o.status == OrderStatus.DELIVERED)
    cancelled = sum(1 for o in orders if o.status == OrderStatus.CANCELLED)
    return VolumeReport(len(orders), delivered, cancelled, len(orders) - delivered - cancelled)


def revenue(all_orders: Iterable[ServiceOrder], period: Period) -> RevenueReport:
    by_method = dict.fromkeys(PAYMENT_METHODS, ZERO)
    delivered_totals: list[Decimal] = []
    for order in all_orders:
        for payment in order.payments:
            if period.contains(payment.paid_at):
                by_method[payment.method] = quantize(by_method[payment.method] + payment.amount)
        delivered_at = _first_status_event(order, OrderStatus.DELIVERED)
        if delivered_at and period.contains(delivered_at) and order.status == OrderStatus.DELIVERED:
            delivered_totals.append(compute_totals(order).total)
    average = quantize(sum(delivered_totals, ZERO) / len(delivered_totals)) if delivered_totals else None
    return RevenueReport(quantize(sum(by_method.values(), ZERO)), by_method, len(delivered_totals), average)


def technician_rows(orders: list[ServiceOrder], technicians: Iterable[Technician]) -> tuple[TechnicianRow, ...]:
    rows = []
    for technician in technicians:
        mine = [o for o in orders if o.technician_id == technician.id]
        if mine:
            rows.append(
                TechnicianRow(
                    name=technician.name,
                    assigned=len(mine),
                    finished=sum(1 for o in mine if o.status in FINISHED),
                    budget_total=quantize(sum((compute_totals(o).total for o in mine), ZERO)),
                )
            )
    return tuple(sorted(rows, key=lambda r: (-r.finished, -r.assigned, r.name)))


def turnaround(orders: list[ServiceOrder]) -> TurnaroundReport:
    durations = []
    for order in orders:
        done_at = _first_status_event(order, OrderStatus.DONE)
        if done_at:
            durations.append((done_at - order.opened_at).total_seconds() / 86_400)
    if not durations:
        return TurnaroundReport(None, 0)
    return TurnaroundReport(round(sum(durations) / len(durations), 1), len(durations))


def build_report(
    all_orders: list[ServiceOrder], technicians: Iterable[Technician], period: Period
) -> OperationalReport:
    in_period = [o for o in all_orders if period.contains(o.opened_at)]
    return OperationalReport(
        period=period,
        volume=volume(in_period),
        revenue=revenue(all_orders, period),
        technicians=technician_rows(in_period, technicians),
        turnaround=turnaround(in_period),
    )


def orders_in_period(all_orders: Iterable[ServiceOrder], period: Period) -> list[ServiceOrder]:
    return sorted((o for o in all_orders if period.contains(o.opened_at)), key=lambda o: (o.opened_at, o.code))
