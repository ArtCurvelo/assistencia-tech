"""Evolução mensal dos relatórios (mudança improve-reports)."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.reports import monthly_series
from assistencia_tech.models import Payment
from assistencia_tech.presenters import monthly_chart

pytestmark = pytest.mark.anyio


async def orders():
    return await build_demo_gateway(lambda: 2026).orders.list()


async def test_six_months_including_empty_ones():
    series = monthly_series(await orders(), date(2026, 11, 9))
    assert [(p.year, p.month) for p in series] == [(2026, m) for m in range(6, 12)]
    october = next(p for p in series if p.month == 10)
    assert october.opened == 7  # o seed da demonstração abre as 7 ordens em outubro
    assert next(p for p in series if p.month == 8).opened == 0


async def test_year_turn():
    series = monthly_series([], date(2027, 2, 1))
    assert [(p.year, p.month) for p in series] == [(2026, 9), (2026, 10), (2026, 11), (2026, 12), (2027, 1), (2027, 2)]


async def test_received_by_payment_month_and_delivered_by_delivery_date():
    data = await orders()
    order = data[0]
    payments = (Payment(id="a", amount="100,00", method="PIX", paid_at=datetime(2026, 11, 2, 10, tzinfo=BRT)),
                Payment(id="b", amount="50,00", method="PIX", paid_at=datetime(2026, 9, 2, 10, tzinfo=BRT)))
    series = monthly_series([order.model_copy(update={"payments": payments})], date(2026, 11, 9))
    received = {p.month: p.received for p in series}
    assert received[11] == Decimal("100.00") and received[9] == Decimal("50.00") and received[10] == Decimal("0")
    delivered = monthly_series(data, date(2026, 11, 9))
    assert sum(p.delivered for p in delivered) == 1  # OS-2026-00120 entregue em outubro


def test_chart_labels():
    series = monthly_series([], date(2027, 1, 15), months=2)
    assert [row["mes"] for row in monthly_chart(series)] == ["dez/26", "jan/27"]
