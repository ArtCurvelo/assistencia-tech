import pytest

from assistencia_tech.data.demo import build_demo_gateway, next_order_code
from assistencia_tech.data.errors import NotFoundError, ValidationError
from assistencia_tech.data.repositories import (
    ClientRepository,
    DataGateway,
    EquipmentRepository,
    OrderRepository,
)
from assistencia_tech.models import ClientCreate, EquipmentCreate, OrderCreate

pytestmark = pytest.mark.anyio


@pytest.fixture
def gateway() -> DataGateway:
    return build_demo_gateway(year_provider=lambda: 2026)


async def test_demo_gateway_satisfies_interfaces(gateway):
    assert gateway.is_demo and gateway.source == "demo"
    assert isinstance(gateway.clients, ClientRepository)
    assert isinstance(gateway.equipment, EquipmentRepository)
    assert isinstance(gateway.orders, OrderRepository)


async def test_seed_data_is_loaded(gateway):
    assert len(await gateway.clients.list()) == 3
    assert len(await gateway.equipment.list()) == 3
    assert len(await gateway.orders.list()) == 3


async def test_gateways_are_independent():
    first = build_demo_gateway()
    await first.clients.create(ClientCreate(name="Novo", email="novo@exemplo.test"))
    assert len(await build_demo_gateway().clients.list()) == 3


async def test_create_client_appears_in_list(gateway):
    created = await gateway.clients.create(ClientCreate(name="Ana", email="ana@exemplo.test"))
    assert created.id == "4"
    assert created in await gateway.clients.list()


async def test_duplicate_email_is_rejected(gateway):
    with pytest.raises(ValidationError):
        await gateway.clients.create(ClientCreate(name="Outra", email="marina@example.test"))


async def test_equipment_requires_existing_client(gateway):
    with pytest.raises(ValidationError):
        await gateway.equipment.create(EquipmentCreate(client="Ninguém", kind="Notebook", model="X"))
    created = await gateway.equipment.create(
        EquipmentCreate(client="Marina Oliveira", kind="Notebook", model="Dell")
    )
    assert created.id == "4"


async def test_new_order_follows_last_code(gateway):
    order = await gateway.orders.create(
        OrderCreate(client="Marina Oliveira", device="Notebook", problem="Não liga")
    )
    assert order.code == "OS-2026-00126"
    assert order.status == "Recebido"
    assert (await gateway.orders.list())[0] == order
    second = await gateway.orders.create(OrderCreate(client="Camila Souza", device="Celular", problem="Tela"))
    assert second.code == "OS-2026-00127"


async def test_order_requires_existing_client(gateway):
    with pytest.raises(ValidationError):
        await gateway.orders.create(OrderCreate(client="Ninguém", device="X", problem="Y"))


async def test_get_by_code_is_case_insensitive(gateway):
    order = await gateway.orders.get_by_code(" os-2026-00125 ")
    assert order.code == "OS-2026-00125"


async def test_get_unknown_code_raises_not_found(gateway):
    with pytest.raises(NotFoundError):
        await gateway.orders.get_by_code("OS-1999-00001")


async def test_update_status(gateway):
    updated = await gateway.orders.update_status("OS-2026-00125", "Concluído")
    assert updated.status == "Concluído"
    assert (await gateway.orders.get_by_code("OS-2026-00125")).status == "Concluído"


async def test_invalid_status_keeps_previous_value(gateway):
    with pytest.raises(ValidationError):
        await gateway.orders.update_status("OS-2026-00125", "Perdido")
    assert (await gateway.orders.get_by_code("OS-2026-00125")).status == "Em reparo"


async def test_update_status_unknown_order(gateway):
    with pytest.raises(NotFoundError):
        await gateway.orders.update_status("OS-2026-99999", "Concluído")


def test_next_order_code_rules():
    assert next_order_code(["OS-2026-00125"], 2026) == "OS-2026-00126"
    assert next_order_code(["OS-2026-126", "OS-2026-00009"], 2026) == "OS-2026-00127"
    assert next_order_code(["OS-2025-00500"], 2026) == "OS-2026-00001"
    assert next_order_code([], 2027) == "OS-2027-00001"
