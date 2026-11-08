"""Comprovante da ordem com QR code (mudança add-order-receipt)."""

from urllib.parse import unquote

import pytest
import segno

from assistencia_tech.config import ConfigurationError, load_settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import AuthenticationError, NotFoundError, PermissionDeniedError
from assistencia_tech.domain import receipt
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.presenters import receipt_row
from assistencia_tech.services import OrderService, PortalService

pytestmark = pytest.mark.anyio

BASE = "https://assistencia.exemplo.com.br"
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)
TECH = Principal("3", "Carlos", "c@x.test", Role.TECHNICIAN, technician_id="1")
DELIVERED = "OS-2026-00120"  # concluída e entregue no seed
CANCELLED = "OS-2026-00121"
REPAIR = "OS-2026-00125"


async def receipt_of(code, principal=ATTENDANT):
    return await OrderService(build_demo_gateway(lambda: 2026), principal).receipt(code)


# ----------------------------------------------------------------------
# Domínio
# ----------------------------------------------------------------------
def test_code_format_is_checked_before_any_lookup():
    assert receipt.normalize_code(" os-2026-00125 ") == "OS-2026-00125"
    for junk in ("", "qualquer-coisa", "OS-2026-12", "OS-2026-00125/../x", "OS-2026-00125 OR 1=1"):
        assert receipt.normalize_code(junk) is None


def test_public_base_url_prefers_configuration():
    assert receipt.public_base_url(BASE + "/", "http://localhost:3000") == BASE
    assert receipt.public_base_url(None, "http://localhost:3000/admin/x?y=1") == "http://localhost:3000"
    assert receipt.public_base_url(None, "javascript:alert(1)") == ""
    assert receipt.public_base_url(None, "") == ""


def test_tracking_url_and_qr_code():
    url = receipt.tracking_url(BASE, "OS-2026-00125")
    assert url == f"{BASE}/consulta/OS-2026-00125"
    uri = receipt.qr_svg_data_uri(url)
    assert uri.startswith("data:image/svg+xml")
    svg = unquote(uri.split(",", 1)[1])
    assert svg.startswith("<svg") and "path" in svg
    # Mesma matriz que o segno gera para o endereço: o QR code codifica exatamente a URL.
    assert uri == segno.make(url, error="m", micro=False).svg_data_uri(scale=4, border=2, dark="#000", light="#fff")


def test_public_url_setting():
    assert load_settings({"ASSISTENCIA_PUBLIC_URL": f" {BASE}/ "}).public_url == BASE
    assert load_settings({}).public_url is None
    with pytest.raises(ConfigurationError, match="http"):
        load_settings({"ASSISTENCIA_PUBLIC_URL": "assistencia.exemplo.com.br"})


# ----------------------------------------------------------------------
# Visão do comprovante
# ----------------------------------------------------------------------
async def test_entry_receipt_for_an_open_order():
    order, client, equipment = await receipt_of(REPAIR)
    row = receipt_row(order, client, equipment, BASE)
    assert row["kind"] == receipt.RECEIPT_ENTRY and row["is_delivery"] == ""
    assert row["client"] == client.name and row["equipment"] == equipment.description
    assert row["problem"] == order.problem and row["due_date"] == f"{order.due_date:%d/%m/%Y}"
    assert row["tracking_url"] == f"{BASE}/consulta/{REPAIR}"


async def test_receipt_never_shows_the_full_cpf():
    order, client, equipment = await receipt_of(REPAIR)
    row = receipt_row(order, client, equipment, BASE)
    assert row["cpf"] == f"***.***.***-{client.cpf[-2:]}"
    assert not any(client.cpf in value for value in row.values())


async def test_delivery_receipt_has_delivery_and_warranty():
    order, client, equipment = await receipt_of(DELIVERED)
    row = receipt_row(order, client, equipment, BASE)
    assert row["kind"] == receipt.RECEIPT_DELIVERY and row["is_delivery"] == "1"
    assert row["delivered_at"] and row["warranty_until"]


async def test_cancelled_receipt_shows_the_reason():
    order, client, equipment = await receipt_of(CANCELLED)
    row = receipt_row(order, client, equipment, BASE)
    assert row["kind"] == receipt.RECEIPT_ENTRY and row["status"] == "Cancelado"
    assert row["cancel_reason"] == order.cancel_reason != ""


async def test_receipt_tolerates_removed_client_and_equipment():
    order, _, _ = await receipt_of(REPAIR)
    row = receipt_row(order, None, None, BASE)
    assert row["client"] == "Cliente removido" and row["cpf"] == "—" and row["serial"] == "—"


# ----------------------------------------------------------------------
# Acesso
# ----------------------------------------------------------------------
async def test_staff_receipt_requires_order_view():
    with pytest.raises(AuthenticationError):
        await receipt_of(REPAIR, principal=None)
    with pytest.raises(PermissionDeniedError):  # cliente usa o portal, não o comprovante da equipe
        await receipt_of(REPAIR, principal=Principal("90", "Dona", "d@x.test", Role.CLIENT, client_id="1"))
    order, _, _ = await receipt_of(REPAIR, principal=TECH)  # técnico consulta qualquer ordem
    assert order.code == REPAIR


async def test_client_only_gets_own_order_for_the_receipt():
    gateway = build_demo_gateway(lambda: 2026)
    order = await gateway.orders.get_by_code(REPAIR)
    owner = Principal("90", "Dona", "d@x.test", Role.CLIENT, client_id=order.client_id)
    stranger = Principal("91", "Outro", "o@x.test", Role.CLIENT,
                         client_id=next(c.id for c in await gateway.clients.list() if c.id != order.client_id))
    assert (await PortalService(gateway, owner).my_order(REPAIR)).order.code == REPAIR
    with pytest.raises(NotFoundError):
        await PortalService(gateway, stranger).my_order(REPAIR)
