"""Quadro Kanban das ordens (mudança add-orders-board)."""

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import ValidationError
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import ORDER_STATUSES, OrderStatus
from assistencia_tech.presenters import BOARD_FINAL_LIMIT, board_columns
from assistencia_tech.services import OrderService
from assistencia_tech.services.catalog import Catalog

pytestmark = pytest.mark.anyio

ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)
CARLOS = Principal("3", "Carlos", "c@x.test", Role.TECHNICIAN, technician_id="1")


async def catalog(gw=None):
    gw = gw or build_demo_gateway(lambda: 2026)
    return Catalog(await gw.clients.list(), await gw.equipment.list(), await gw.technicians.list(),
                   await gw.orders.list())


async def test_one_column_per_status_with_counts():
    data = await catalog()
    columns, cards = board_columns(data, ATTENDANT)
    assert [c["status"] for c in columns] == list(ORDER_STATUSES)
    for column in columns:
        assert int(column["count"]) == sum(1 for o in data.orders if o.status == column["status"])
        assert len(cards[column["status"]]) == int(column["count"])


async def test_moves_follow_permissions_and_never_cancel():
    data = await catalog()
    _, cards = board_columns(data, ATTENDANT)
    awaiting = cards["Aguardando aprovação"][0]
    assert "|Em reparo|" in awaiting["moves"] and "Cancelado" not in awaiting["moves"]
    _, tech_cards = board_columns(data, CARLOS)
    others = [c for c in tech_cards["Em análise"] if c["technician"] != "Carlos Mendes"]
    assert others and all(c["moves"] == "" for c in others)  # ordem de outro técnico: sem botões


async def test_final_columns_show_only_the_latest():
    data = await catalog()
    delivered = next(o for o in data.orders if o.status == OrderStatus.DELIVERED)
    many = [delivered.model_copy(update={"code": f"OS-2026-{900 + i:05d}"}) for i in range(20)]
    columns, cards = board_columns(Catalog(data.clients, data.equipment, data.technicians, data.orders + many),
                                   ATTENDANT)
    column = next(c for c in columns if c["status"] == "Entregue")
    assert len(cards["Entregue"]) == BOARD_FINAL_LIMIT
    assert int(column["count"]) == 21 and column["more"] == str(21 - BOARD_FINAL_LIMIT)


async def test_delivery_without_payment_is_refused_by_the_service():
    gw = build_demo_gateway(lambda: 2026)
    with pytest.raises(ValidationError):
        await OrderService(gw, ATTENDANT).change_status("OS-2026-00122", "Entregue")  # concluída com saldo
    assert (await gw.orders.get_by_code("OS-2026-00122")).status == OrderStatus.DONE
