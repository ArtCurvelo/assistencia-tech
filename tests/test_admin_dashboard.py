"""Painel orientado a ações e site público (mudança improve-services-and-dashboard)."""

import pathlib
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import OrderStatus, Payment
from assistencia_tech.presenters import (
    attention_rows,
    dashboard_metrics,
    greeting,
    received_in_month,
    technician_queue,
)
from assistencia_tech.services.catalog import Catalog

pytestmark = pytest.mark.anyio

ADMIN = Principal("1", "Ana Ribeiro", "a@x.test", Role.ADMIN)
CARLOS = Principal("3", "Carlos Mendes", "c@x.test", Role.TECHNICIAN, technician_id="1")
ROOT = pathlib.Path(__file__).resolve().parent.parent


async def catalog(**changes):
    gw = build_demo_gateway(lambda: 2026)
    orders = await gw.orders.list()
    orders = [changes.get(o.code, lambda x: x)(o) for o in orders]
    return Catalog(await gw.clients.list(), await gw.equipment.list(), await gw.technicians.list(), orders)


def test_greeting_by_time_of_day():
    assert greeting("Ana Ribeiro", datetime(2026, 11, 9, 8, 0, tzinfo=BRT)) == {
        "text": "Bom dia, Ana!", "date": "segunda-feira, 9 de novembro de 2026"}
    assert greeting("Ana", datetime(2026, 11, 9, 14, 0, tzinfo=BRT))["text"] == "Boa tarde, Ana!"
    assert greeting("", datetime(2026, 11, 9, 20, 0, tzinfo=BRT))["text"] == "Boa noite!"


async def test_attention_priority_and_no_duplicates():
    data = await catalog()
    today = max(o.due_date for o in data.orders) + timedelta(days=3)
    rows = attention_rows(data, today)
    codes = [r["code"] for r in rows]
    assert len(codes) == len(set(codes))
    kinds = [r["reason_class"].split("attention-")[-1] for r in rows]
    # atrasadas primeiro, depois prontas, depois aguardando o cliente
    assert kinds == sorted(kinds, key=["late", "ready", "awaiting"].index)
    late = [r for r in rows if r["reason_class"].endswith("late")]
    assert late and late[0]["reason"].startswith("Atrasada há")
    # "Aguardando aprovação" atrasada aparece só uma vez, como atrasada
    awaiting = next(o for o in data.orders if o.status == OrderStatus.AWAITING_APPROVAL)
    assert [r["reason"] for r in rows if r["code"] == awaiting.code][0].startswith("Atrasada")


async def test_nothing_pending_when_all_delivered():
    deliver = lambda o: o.model_copy(update={"status": OrderStatus.DELIVERED})  # noqa: E731
    data = await catalog()
    data = Catalog(data.clients, data.equipment, data.technicians, [deliver(o) for o in data.orders])
    assert attention_rows(data) == []


async def test_technician_queue_only_for_own_open_orders():
    data = await catalog()
    queue = technician_queue(data, CARLOS)
    mine_open = [o for o in data.orders if o.technician_id == "1" and o.status not in
                 (OrderStatus.DONE, OrderStatus.DELIVERED, OrderStatus.CANCELLED)]
    assert [r["code"] for r in queue] == [o.code for o in sorted(mine_open, key=lambda o: o.opened_at)]
    assert technician_queue(data, ADMIN) == []


async def test_received_in_month_counts_only_current_month():
    data = await catalog()
    order = data.orders[0]
    now = datetime(2026, 11, 9, 10, 0, tzinfo=BRT)
    payments = (Payment(id="p1", amount="100,00", method="PIX", paid_at=now),
                Payment(id="p2", amount="50,00", method="PIX", paid_at=now - timedelta(days=40)))
    only = Catalog(data.clients, data.equipment, data.technicians, [order.model_copy(update={"payments": payments})])
    assert received_in_month(only, now.date()) == Decimal("100.00")
    assert "received_month" in dashboard_metrics(data)


def test_home_has_no_admin_shortcut_and_services_explain_the_flow():
    public = (ROOT / "assistencia_tech/pages/public.py").read_text(encoding="utf-8")
    assert "Área administrativa" not in public and 'href="/admin"' not in public
    for text in ("COMO FUNCIONA", "Garantia de 90 dias", "E se eu recusar o orçamento?", "Nada sem a sua aprovação"):
        assert text in public
