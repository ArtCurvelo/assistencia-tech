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
from .rating import NpsSummary, nps_summary
from .validators import quantize

DEFAULT_PERIOD_DAYS = 90
RECENT_COMMENTS = 10
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
    average_rating: float | None = None  # avaliações feitas no período (add-service-rating)


@dataclass(frozen=True)
class TurnaroundReport:
    average_days: float | None
    count: int


@dataclass(frozen=True)
class RatingComment:
    code: str
    score: int
    comment: str
    at: datetime


@dataclass(frozen=True)
class SatisfactionReport:
    summary: NpsSummary
    comments: tuple[RatingComment, ...]


@dataclass(frozen=True)
class OperationalReport:
    period: Period
    volume: VolumeReport
    revenue: RevenueReport
    technicians: tuple[TechnicianRow, ...]
    turnaround: TurnaroundReport
    satisfaction: SatisfactionReport


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


def rated_in(orders: Iterable[ServiceOrder], period: Period) -> list[ServiceOrder]:
    """Ordens avaliadas dentro do período (pela data da avaliação)."""
    return [o for o in orders if o.rating is not None and period.contains(o.rating.at)]


def technician_rows(
    orders: list[ServiceOrder], technicians: Iterable[Technician], rated: Iterable[ServiceOrder] = ()
) -> tuple[TechnicianRow, ...]:
    rated = list(rated)
    rows = []
    for technician in technicians:
        mine = [o for o in orders if o.technician_id == technician.id]
        if mine:
            scores = [o.rating.score for o in rated if o.technician_id == technician.id and o.rating]
            rows.append(
                TechnicianRow(
                    name=technician.name,
                    assigned=len(mine),
                    finished=sum(1 for o in mine if o.status in FINISHED),
                    budget_total=quantize(sum((compute_totals(o).total for o in mine), ZERO)),
                    average_rating=nps_summary(scores).average,
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


def satisfaction(all_orders: Iterable[ServiceOrder], period: Period) -> SatisfactionReport:
    rated = sorted(rated_in(all_orders, period), key=lambda o: o.rating.at, reverse=True)
    comments = tuple(
        RatingComment(o.code, o.rating.score, o.rating.comment, o.rating.at) for o in rated if o.rating.comment
    )[:RECENT_COMMENTS]
    return SatisfactionReport(nps_summary(o.rating.score for o in rated), comments)


def build_report(
    all_orders: list[ServiceOrder], technicians: Iterable[Technician], period: Period
) -> OperationalReport:
    in_period = [o for o in all_orders if period.contains(o.opened_at)]
    return OperationalReport(
        period=period,
        volume=volume(in_period),
        revenue=revenue(all_orders, period),
        technicians=technician_rows(in_period, technicians, rated_in(all_orders, period)),
        turnaround=turnaround(in_period),
        satisfaction=satisfaction(all_orders, period),
    )


def orders_in_period(all_orders: Iterable[ServiceOrder], period: Period) -> list[ServiceOrder]:
    return sorted((o for o in all_orders if period.contains(o.opened_at)), key=lambda o: (o.opened_at, o.code))


# ----------------------------------------------------------------------
# Evolução mensal (improve-reports)
# ----------------------------------------------------------------------
MONTHS_IN_CHART = 6


@dataclass(frozen=True)
class MonthPoint:
    year: int
    month: int
    opened: int
    delivered: int
    received: Decimal


def _shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1


def monthly_series(all_orders: Iterable[ServiceOrder], today: date, months: int = MONTHS_IN_CHART) -> list[MonthPoint]:
    """Últimos ``months`` meses (incluindo o atual): abertas, entregues e recebido em cada mês."""
    keys = [_shift_month(today.year, today.month, -offset) for offset in range(months - 1, -1, -1)]
    opened = dict.fromkeys(keys, 0)
    delivered = dict.fromkeys(keys, 0)
    received = dict.fromkeys(keys, ZERO)

    def key(moment: datetime) -> tuple[int, int]:
        local = moment.astimezone(BRT)
        return local.year, local.month

    for order in all_orders:
        if key(order.opened_at) in opened:
            opened[key(order.opened_at)] += 1
        delivered_at = _first_status_event(order, OrderStatus.DELIVERED)
        if delivered_at and key(delivered_at) in delivered:
            delivered[key(delivered_at)] += 1
        for payment in order.payments:
            if key(payment.paid_at) in received:
                received[key(payment.paid_at)] = quantize(received[key(payment.paid_at)] + payment.amount)
    return [MonthPoint(y, m, opened[(y, m)], delivered[(y, m)], received[(y, m)]) for y, m in keys]
