import pytest

from assistencia_tech.data.demo import build_demo_gateway, next_order_code
from assistencia_tech.data.demo import seed
from assistencia_tech.data.errors import NotFoundError, ValidationError
from assistencia_tech.data.repositories import (
    ClientRepository,
    EquipmentRepository,
    OrderRepository,
    TechnicianRepository,
)
from assistencia_tech.models import ClientCreate

pytestmark = pytest.mark.anyio


@pytest.fixture
def gateway():
    return build_demo_gateway(year_provider=lambda: 2026)


async def test_demo_gateway_satisfies_interfaces(gateway):
    assert gateway.is_demo and gateway.source == "demo"
    assert isinstance(gateway.clients, ClientRepository)
    assert isinstance(gateway.equipment, EquipmentRepository)
    assert isinstance(gateway.technicians, TechnicianRepository)
    assert isinstance(gateway.orders, OrderRepository)


async def test_seed_sizes(gateway):
    assert len(await gateway.clients.list()) == 6
    assert len(await gateway.equipment.list()) == 8
    assert len(await gateway.technicians.list()) == 3
    assert len(await gateway.orders.list()) == 7


async def test_gateways_are_independent():
    first = build_demo_gateway()
    await first.clients.create(
        ClientCreate(name="Novo", cpf="52998224725", email="novo@exemplo.test", phone="11987654321")
    )
    assert len(await build_demo_gateway().clients.list()) == 6


async def test_crud_roundtrip(gateway):
    created = await gateway.clients.create(
        ClientCreate(name="Ana", cpf="52998224725", email="ana@exemplo.test", phone="11987654321")
    )
    assert created.id == "7"
    renamed = await gateway.clients.update(created.model_copy(update={"name": "Ana Paula"}))
    assert (await gateway.clients.get("7")).name == renamed.name == "Ana Paula"
    await gateway.clients.delete("7")
    with pytest.raises(NotFoundError):
        await gateway.clients.get("7")


async def test_orders_listed_newest_first(gateway):
    codes = [o.code for o in await gateway.orders.list()]
    assert codes[0] == "OS-2026-00126" and codes[-1] == "OS-2026-00120"


async def test_next_code_and_duplicate_protection(gateway):
    assert await gateway.orders.next_code() == "OS-2026-00127"
    existing = await gateway.orders.get_by_code("os-2026-00125")
    with pytest.raises(ValidationError):
        await gateway.orders.create(existing)


async def test_get_unknown_code_raises_not_found(gateway):
    with pytest.raises(NotFoundError):
        await gateway.orders.get_by_code("OS-1999-00001")


def test_next_order_code_rules():
    assert next_order_code(["OS-2026-00125"], 2026) == "OS-2026-00126"
    assert next_order_code(["OS-2026-126", "OS-2026-00009"], 2026) == "OS-2026-00127"
    assert next_order_code(["OS-2025-00500"], 2026) == "OS-2026-00001"
    assert next_order_code([], 2027) == "OS-2027-00001"


def test_seed_covers_every_status_and_respects_links():
    clients = {c.id for c in seed.seed_clients()}
    equipment = {e.id: e for e in seed.seed_equipment()}
    technicians = {t.id for t in seed.seed_technicians()}
    orders = seed.seed_orders()
    assert {o.status.value for o in orders} == {
        "Recebido", "Em análise", "Aguardando aprovação", "Em reparo", "Concluído", "Entregue", "Cancelado"
    }
    assert all(e.client_id in clients for e in equipment.values())
    for order in orders:
        assert order.client_id in clients
        assert equipment[order.equipment_id].client_id == order.client_id
        assert order.technician_id is None or order.technician_id in technicians
        times = [event.at for event in order.history]
        assert times == sorted(times), f"histórico fora de ordem em {order.code}"
        assert order.updated_at == times[-1]
