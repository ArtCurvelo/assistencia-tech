"""Estoque de peças (mudança add-parts-inventory): domínio, serviço sobre a demonstração e adaptador Xano."""

import json
from datetime import datetime
from decimal import Decimal

import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import PermissionDeniedError, ValidationError
from assistencia_tech.data.request_context import use_backend_token
from assistencia_tech.data.xano import XanoClient, build_xano_gateway, mappers
from assistencia_tech.data.xano.inventory import movement_from, part_from
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.inventory import ensure_available, needs_restock, stock_effects, stock_level
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import ItemKind, MovementKind, OrderItem, OrderStatus, Part, StockLevel
from assistencia_tech.services import InventoryService, OrderService, PortalService

pytestmark = pytest.mark.anyio

ADMIN = Principal("1", "Ana", "a@x.test", Role.ADMIN)
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)
TECH = Principal("3", "Carlos", "c@x.test", Role.TECHNICIAN, technician_id="1")
ANALYSIS = "OS-2026-00124"  # Em análise, técnico 2 no seed
AWAITING = "OS-2026-00123"  # Aguardando aprovação, cliente 4 no seed


def part(quantity=5, minimum=2, active=True) -> Part:
    return Part(id="9", code="x-1", name="Peça X", unit_price=Decimal("10"), quantity=quantity,
                min_quantity=minimum, active=active)


# ----------------------------------------------------------------------
# Domínio
# ----------------------------------------------------------------------
def test_stock_levels():
    assert stock_level(part(0)) == StockLevel.OUT
    assert stock_level(part(2)) == StockLevel.LOW
    assert stock_level(part(3)) == StockLevel.NORMAL
    assert needs_restock(part(1)) and not needs_restock(part(1, active=False))
    assert part().code == "X-1"  # código em maiúsculas


def test_ensure_available():
    ensure_available(part(2), 2)
    with pytest.raises(ValidationError, match="2 unidades disponíveis"):
        ensure_available(part(2), 3)
    with pytest.raises(ValidationError, match="inativa"):
        ensure_available(part(5, active=False), 1)


async def test_stock_effects_for_add_remove_and_cancel():
    order = await build_demo_gateway(lambda: 2026).orders.get_by_code(ANALYSIS)
    item = OrderItem(id="99", kind=ItemKind.PART, description="Peça X", quantity=2, unit_price=Decimal("10"),
                     part_id="9")
    with_item = order.model_copy(update={"items": (*order.items, item)})
    [effect] = stock_effects(order, with_item)
    assert (effect.part_id, effect.kind, effect.quantity) == ("9", MovementKind.OUT, 2)
    back = stock_effects(with_item, order)
    assert [(e.kind, e.quantity) for e in back] == [(MovementKind.RETURN, 2)]
    cancelled = with_item.model_copy(update={"status": OrderStatus.CANCELLED})
    assert [(e.kind, e.quantity) for e in stock_effects(with_item, cancelled)] == [(MovementKind.RETURN, 2)]
    assert stock_effects(cancelled, cancelled) == []  # não devolve duas vezes


# ----------------------------------------------------------------------
# Serviço sobre o modo demonstração
# ----------------------------------------------------------------------
async def _part(gateway, part_id):
    return await gateway.parts.get(part_id)


async def test_create_restock_and_movements():
    gateway = build_demo_gateway(lambda: 2026)
    service = InventoryService(gateway, ATTENDANT)
    created = await service.create({"code": "hd-1tb", "name": "HD 1 TB", "unit_price": "320,00", "min_quantity": "1"})
    assert (created.code, created.quantity) == ("HD-1TB", 0)
    with pytest.raises(ValidationError, match="Já existe uma peça com o código HD-1TB"):
        await service.create({"code": "HD-1TB", "name": "Outro", "unit_price": "1"})
    updated = await service.restock(created.id, "5", "NF 77")
    assert updated.quantity == 5
    move = (await service.movements())[0]
    assert (move.kind, move.quantity, move.author, move.note) == (MovementKind.IN, 5, "Bia (Atendente)", "NF 77")
    with pytest.raises(ValidationError, match="maior que zero"):
        await service.restock(created.id, "0")


async def test_edit_never_changes_quantity():
    gateway = build_demo_gateway(lambda: 2026)
    service = InventoryService(gateway, ADMIN)
    edited = await service.update("1", {"code": "SSD-480", "name": "SSD 480 GB SATA", "unit_price": "260,00",
                                        "min_quantity": "2", "quantity": "999"})
    assert edited.name == "SSD 480 GB SATA" and edited.quantity == 6


async def test_technician_views_but_cannot_manage():
    gateway = build_demo_gateway(lambda: 2026)
    assert await InventoryService(gateway, TECH).list()
    with pytest.raises(PermissionDeniedError):
        await InventoryService(gateway, TECH).restock("1", "1")


async def test_catalog_part_uses_catalog_data_and_consumes_stock():
    gateway = build_demo_gateway(lambda: 2026)
    order = await OrderService(gateway, ADMIN).add_item(ANALYSIS, {"kind": "Peça", "part_id": "1", "quantity": "2"})
    item = order.items[-1]
    assert (item.description, item.unit_price, item.quantity, item.part_id) == ("SSD 480 GB", Decimal("250.00"), 2, "1")
    assert (await _part(gateway, "1")).quantity == 4
    move = (await gateway.parts.movements())[0]
    assert (move.kind, move.order_code, move.author) == (MovementKind.OUT, ANALYSIS, "Ana (Administrador)")


async def test_insufficient_stock_adds_nothing():
    gateway = build_demo_gateway(lambda: 2026)
    with pytest.raises(ValidationError, match="Estoque insuficiente de Bateria 6 células: 1 unidade disponível"):
        await OrderService(gateway, ADMIN).add_item(ANALYSIS, {"kind": "Peça", "part_id": "4", "quantity": "2"})
    assert (await _part(gateway, "4")).quantity == 1
    assert not any(i.part_id for i in (await gateway.orders.get_by_code(ANALYSIS)).items)


async def test_removing_the_item_returns_the_stock():
    gateway = build_demo_gateway(lambda: 2026)
    service = OrderService(gateway, ADMIN)
    order = await service.add_item(ANALYSIS, {"kind": "Peça", "part_id": "2", "quantity": "1"})
    await service.remove_item(ANALYSIS, order.items[-1].id)
    assert (await _part(gateway, "2")).quantity == 3
    assert (await gateway.parts.movements())[0].kind == MovementKind.RETURN


async def test_cancellation_returns_the_stock():
    gateway = build_demo_gateway(lambda: 2026)
    service = OrderService(gateway, ADMIN)
    await service.add_item(ANALYSIS, {"kind": "Peça", "part_id": "6", "quantity": "2"})
    assert (await _part(gateway, "6")).quantity == 2
    await service.change_status(ANALYSIS, "Cancelado", "Cliente desistiu")
    assert (await _part(gateway, "6")).quantity == 4


async def test_client_refusal_returns_the_stock():
    gateway = build_demo_gateway(lambda: 2026)
    order = await gateway.orders.get_by_code(AWAITING)
    stocked = OrderItem(id="50", kind=ItemKind.PART, description="Fonte", quantity=1, unit_price=Decimal("180"),
                        part_id="2")
    await gateway.orders.save(order.model_copy(update={"items": (*order.items, stocked)}))
    assert (await _part(gateway, "2")).quantity == 2
    client = Principal("40", "Rafael", "r@x.test", Role.CLIENT, client_id="4")
    await PortalService(gateway, client).decide_budget(AWAITING, False, "Caro demais")
    assert (await _part(gateway, "2")).quantity == 3


async def test_loose_part_does_not_touch_stock():
    gateway = build_demo_gateway(lambda: 2026)
    before = [p.quantity for p in await gateway.parts.list()]
    await OrderService(gateway, ADMIN).add_item(
        ANALYSIS, {"kind": "Peça", "description": "Cabo flat", "quantity": "1", "unit_price": "45,00"})
    assert [p.quantity for p in await gateway.parts.list()] == before


# ----------------------------------------------------------------------
# Adaptador Xano
# ----------------------------------------------------------------------
CREATED = int(datetime(2026, 11, 7, 10, 0, tzinfo=BRT).timestamp() * 1000)
PECA = {"id": 3, "codigo": "SSD-480", "nome": "SSD 480 GB", "preco": 250, "quantidade": 4, "estoque_minimo": 2,
        "ativo": True}


def test_xano_mapping():
    p = part_from(PECA)
    assert (p.id, p.code, p.unit_price, p.quantity, p.min_quantity) == ("3", "SSD-480", Decimal("250.00"), 4, 2)
    move = movement_from({"id": 1, "created_at": CREATED, "peca_id": 3, "tipo": "saida", "quantidade": 1,
                          "os_servicos_id": 12, "autor": "Ana (Administrador)", "observacao": None,
                          "_ordem": {"id": 12, "created_at": CREATED}})
    assert (move.kind, move.order_code, move.note) == (MovementKind.OUT, "OS-2026-00012", "")
    item = OrderItem(id="1", kind=ItemKind.PART, description="SSD", quantity=1, unit_price=Decimal("250"), part_id="3")
    assert mappers.item_payload("12", item)["peca_id"] == 3
    loose = item.model_copy(update={"part_id": ""})
    assert "peca_id" not in mappers.item_payload("12", loose)


async def test_xano_restock_and_list():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.split("/api:", 1)[1].split("/", 1)[1]
        calls.append((request.method, path, json.loads(request.content) if request.content else None))
        if path == "estoque/entrada":
            return httpx.Response(200, json={**PECA, "quantidade": 9})
        if path == "pecas":
            return httpx.Response(200, json=[PECA])
        return httpx.Response(404, json={"message": ""})

    client = XanoClient("https://exemplo.invalid", 5, transport=httpx.MockTransport(handler),
                        pacer=RequestPacer(10_000, 1), cache=ResponseCache(0))
    gateway = build_xano_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"), client=client)
    use_backend_token("jwt")
    try:
        updated = await InventoryService(gateway, ATTENDANT).restock("3", "5", "NF 9")
    finally:
        use_backend_token(None)
    assert updated.quantity == 9
    assert ("POST", "estoque/entrada", {"peca_id": 3, "quantidade": 5, "observacao": "NF 9"}) in calls
