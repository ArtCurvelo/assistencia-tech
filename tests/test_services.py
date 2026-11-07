"""Serviços de aplicação contra o modo demonstração (cenários das specs)."""

from datetime import datetime

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import NotFoundError, ValidationError
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import OrderStatus
from assistencia_tech.services import ClientService, EquipmentService, OrderService, load_catalog

pytestmark = pytest.mark.anyio
NOW = datetime(2026, 11, 6, 15, 30, tzinfo=BRT)
ADMIN = Principal("1", "Ana Ribeiro", "admin@assistencia.test", Role.ADMIN)
NEW_CLIENT = {"name": "Ana Costa", "cpf": "52998224725", "email": "ana@exemplo.test", "phone": "11987654321"}


@pytest.fixture
def gw():
    return build_demo_gateway(year_provider=lambda: 2026)


@pytest.fixture
def clients(gw):
    return ClientService(gw, ADMIN)


@pytest.fixture
def equipment(gw):
    return EquipmentService(gw, ADMIN)


@pytest.fixture
def orders(gw):
    return OrderService(gw, ADMIN, clock=lambda: NOW)


# ---------------------------------------------------------------- clientes
async def test_create_client_and_format(clients):
    created = await clients.create({**NEW_CLIENT, "cpf": "529.982.247-25"})
    assert created.id == "7" and created.cpf == "52998224725"


async def test_duplicate_cpf_and_email(clients):
    await clients.create(NEW_CLIENT)
    with pytest.raises(ValidationError, match="CPF 529.982.247-25"):
        await clients.create({**NEW_CLIENT, "email": "outra@exemplo.test"})
    with pytest.raises(ValidationError, match="e-mail"):
        await clients.create({**NEW_CLIENT, "cpf": "123.456.789-09", "email": "ANA@exemplo.test"})


async def test_edit_client_keeps_links_and_checks_uniqueness(gw, clients):
    updated = await clients.update("1", {"name": "Marina O. Silva", "cpf": "39053344705",
                                         "email": "marina@example.test", "phone": "11988881001"})
    assert updated.name == "Marina O. Silva"
    catalog = await load_catalog(gw, ADMIN)
    assert catalog.clients_by_id[catalog.orders[1].client_id].name == "Marina O. Silva"
    with pytest.raises(ValidationError, match="e-mail"):
        await clients.update("1", {"name": "Marina", "cpf": "39053344705",
                                   "email": "rafael@example.test", "phone": "11988881001"})
    assert (await clients.get("1")).email == "marina@example.test"


async def test_delete_client_blocked_by_links(clients):
    with pytest.raises(ValidationError) as info:
        await clients.delete("4")
    assert "2 equipamentos e 2 ordens de serviço" in info.value.user_message
    removed = await clients.delete("6")  # Lucas não tem vínculos
    assert removed.name == "Lucas Almeida"
    with pytest.raises(NotFoundError):
        await clients.get("6")


async def test_client_detail_history_newest_first(clients):
    detail = await clients.detail("4")
    assert [o.code for o in detail.orders] == ["OS-2026-00123", "OS-2026-00121"]
    assert {e.id for e in detail.equipment} == {"4", "6"}
    with pytest.raises(NotFoundError):
        await clients.detail("999")


# ------------------------------------------------------------ equipamentos
async def test_create_equipment_requires_existing_client(equipment):
    with pytest.raises(NotFoundError, match="Cliente"):
        await equipment.create({"client_id": "999", "kind": "Notebook", "brand": "Lenovo", "model": "IdeaPad 3"})
    created = await equipment.create({"client_id": "6", "kind": "Notebook", "brand": "Lenovo", "model": "IdeaPad 3"})
    assert created.id == "9"


async def test_serial_number_unique_but_optional(equipment):
    with pytest.raises(ValidationError, match="número de série"):
        await equipment.create({"client_id": "6", "kind": "Console", "brand": "Sony",
                                "model": "PS5", "serial_number": " ps5-cfi-1214 "})
    for _ in range(2):
        await equipment.create({"client_id": "6", "kind": "Outro", "brand": "JBL", "model": "Flip 6"})


async def test_change_client_blocked_when_equipment_has_orders(equipment):
    form = {"client_id": "2", "kind": "Notebook", "brand": "Lenovo", "model": "IdeaPad 3 Gen 6",
            "serial_number": "PF3XK21A"}
    with pytest.raises(ValidationError, match="não pode ser alterado"):
        await equipment.update("1", form)
    updated = await equipment.update("1", {**form, "client_id": "1"})
    assert updated.model == "IdeaPad 3 Gen 6"
    moved = await equipment.update("8", {"client_id": "6", "kind": "Console", "brand": "Sony",
                                         "model": "PlayStation 5", "serial_number": "PS5-CFI-1214"})
    assert moved.client_id == "6"


async def test_delete_equipment_blocked_by_orders(equipment):
    with pytest.raises(ValidationError, match="1 ordem de serviço vinculada"):
        await equipment.delete("1")
    await equipment.delete("8")


async def test_equipment_history(equipment):
    eq, history = await equipment.history("4")
    assert eq.model == "OptiPlex 3080" and [o.code for o in history] == ["OS-2026-00123"]


# ------------------------------------------------------------------ ordens
async def test_open_order_rejects_equipment_of_other_client(orders):
    with pytest.raises(ValidationError, match="não pertence ao cliente Lucas Almeida"):
        await orders.open({"client_id": "6", "equipment_id": "1", "problem": "Não liga"})


async def test_open_order_generates_code_and_history(orders):
    order = await orders.open({"client_id": "1", "equipment_id": "8", "problem": "Controle sem resposta"})
    assert order.code == "OS-2026-00127"
    assert order.status == OrderStatus.RECEIVED and order.opened_at == NOW
    assert order.history[0].author == "Ana Ribeiro (Administrador)"


async def test_full_flow_through_service(orders):
    code = "OS-2026-00126"  # Recebido, sem técnico
    with pytest.raises(ValidationError, match="técnico"):
        await orders.change_status(code, "Em análise")
    await orders.assign_technician(code, "3")
    await orders.change_status(code, "Em análise")
    await orders.record_diagnosis(code, "Leitor de chip danificado.")
    await orders.add_item(code, {"kind": "Serviço", "description": "Troca do leitor", "unit_price": "120,00"})
    await orders.add_item(code, {"kind": "Peça", "description": "Leitor de chip", "quantity": "2",
                                 "unit_price": "45,50"})
    await orders.change_status(code, "Aguardando aprovação")
    await orders.change_status(code, "Em reparo")
    await orders.change_status(code, "Concluído")
    await orders.add_payment(code, {"amount": "100,00", "method": "PIX"})
    with pytest.raises(ValidationError, match="R\\$ 111,00"):
        await orders.change_status(code, "Entregue")
    with pytest.raises(ValidationError, match="excede"):
        await orders.add_payment(code, {"amount": "200", "method": "PIX"})
    await orders.add_payment(code, {"amount": "111,00", "method": "Cartão de débito"})
    final = await orders.change_status(code, "Entregue")
    assert final.status == OrderStatus.DELIVERED
    assert final.updated_at == NOW
    assert len(final.history) == 12  # abertura + 11 alterações


async def test_unknown_technician(orders):
    with pytest.raises(NotFoundError):
        await orders.assign_technician("OS-2026-00126", "99")
    with pytest.raises(ValidationError):
        await orders.assign_technician("OS-2026-00126", "")


async def test_remove_item_via_service(orders):
    order = await orders.remove_item("OS-2026-00125", "2")
    assert [i.description for i in order.items] == ["Limpeza interna e troca de pasta térmica"]


async def test_public_view_has_no_personal_data(orders):
    view = await orders.public_view(" os-2026-00125 ")
    dumped = view.model_dump()
    assert set(dumped) == {"code", "status", "equipment", "updated_at", "due_date"}  # previsão: add-deadlines-and-warranty
    assert dumped["status"] == "Em reparo" and dumped["equipment"] == "Notebook Lenovo IdeaPad 3"
    assert "Marina" not in str(dumped)
    with pytest.raises(NotFoundError):
        await orders.public_view("OS-1999-00001")
    with pytest.raises(ValidationError):
        await orders.public_view("  ")
