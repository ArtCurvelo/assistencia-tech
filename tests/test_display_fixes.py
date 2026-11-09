"""Pendências de exibição: autor com parênteses, saldo de ordem cancelada e horário do pagamento."""

from datetime import datetime

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.xano import mappers
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.presenters import totals_row

pytestmark = pytest.mark.anyio


def test_display_name_without_double_parentheses():
    assert Principal("1", "Ana Ribeiro", "a@x.test", Role.ADMIN).display_name == "Ana Ribeiro (Administrador)"
    assert Principal("4", "Carlos Mendes (teste)", "c@x.test", Role.TECHNICIAN).display_name == \
        "Carlos Mendes (teste) · Técnico"


async def test_cancelled_order_has_no_balance_due():
    gw = build_demo_gateway(lambda: 2026)
    cancelled = await gw.orders.get_by_code("OS-2026-00121")
    row = totals_row(cancelled)
    assert (row["balance_label"], row["balance"]) == ("Saldo", "Não se aplica")
    open_row = totals_row(await gw.orders.get_by_code("OS-2026-00125"))
    assert open_row["balance_label"] == "Saldo devedor" and open_row["balance"].startswith("R$")


def test_payment_keeps_the_registration_time_on_the_same_day():
    created = int(datetime(2026, 11, 9, 14, 37, tzinfo=BRT).timestamp() * 1000)
    same_day = mappers.payment_from({"id": 1, "created_at": created, "valor_a_ser_pago": 50,
                                     "forma_de_pagamento": "PIX", "data_do_pagamento": "2026-11-09"})
    assert same_day.paid_at == datetime(2026, 11, 9, 14, 37, tzinfo=BRT)
    other_day = mappers.payment_from({"id": 2, "created_at": created, "valor_a_ser_pago": 50,
                                      "forma_de_pagamento": "PIX", "data_do_pagamento": "2026-11-01"})
    assert other_day.paid_at == datetime(2026, 11, 1, tzinfo=BRT)
