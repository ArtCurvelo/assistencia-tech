"""Autoatendimento do cliente e avisos (mudança add-client-self-service)."""

import json
from datetime import date, datetime, timedelta

import httpx
import pytest

from assistencia_tech.config import Settings, load_settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import ConfigurationError, PermissionDeniedError, ValidationError
from assistencia_tech.data.request_context import use_backend_token
from assistencia_tech.data.xano import XanoClient, build_xano_gateway, mappers
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache
from assistencia_tech.domain import deadlines, notifications, service_request
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import DELIVERY_COURIER, DELIVERY_STORE, Client, OrderStatus
from assistencia_tech.presenters import attention_rows
from assistencia_tech.services import OrderService, PortalService
from assistencia_tech.services import notifications as notify
from assistencia_tech.services.catalog import Catalog

pytestmark = pytest.mark.anyio

AT = datetime(2026, 11, 16, 10, 0, tzinfo=BRT)
MARINA = Principal("6", "Marina Oliveira", "marina@example.test", Role.CLIENT, client_id="1")
RAFAEL = Principal("7", "Rafael Santos", "rafael@example.test", Role.CLIENT, client_id="2")
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)
TECH = Principal("3", "Carlos", "c@x.test", Role.TECHNICIAN, technician_id="1")
ADMIN = Principal("1", "Ana", "a@x.test", Role.ADMIN)
STORE = {"equipment_id": "1", "problem": "Não liga", "delivery_mode": DELIVERY_STORE}
COURIER = {"equipment_id": "1", "problem": "Não liga", "delivery_mode": DELIVERY_COURIER,
           "pickup_address": "Rua das Flores, 100 - Centro", "pickup_period": "Tarde"}


def portal(principal=MARINA, gateway=None):
    return PortalService(gateway or build_demo_gateway(lambda: 2026), principal, clock=lambda: AT)


class FakeNotifier:
    enabled = True

    def __init__(self, fail=False):
        self.sent, self.fail = [], fail

    async def send(self, to_email, to_name, message):
        if self.fail:
            raise httpx.ConnectError("fora do ar")
        self.sent.append((to_email, message))
        return True


@pytest.fixture
def notifier():
    fake = FakeNotifier()
    notify.set_notifier(fake)
    yield fake
    notify.set_notifier(None)


# ----------------------------------------------------------------------
# Regras da solicitação
# ----------------------------------------------------------------------
def test_delivery_validation():
    assert service_request.parse_delivery(STORE) == (DELIVERY_STORE, "", "")
    assert service_request.parse_delivery(COURIER) == (DELIVERY_COURIER, "Rua das Flores, 100 - Centro", "Tarde")
    for form, match in (({}, "forma de entrega"), ({**COURIER, "pickup_address": " "}, "endereço de coleta"),
                        ({**COURIER, "pickup_address": "x" * 201}, "200"),
                        ({**COURIER, "pickup_period": "Madrugada"}, "período")):
        with pytest.raises(ValidationError, match=match):
            service_request.parse_delivery(form)


def test_store_info_never_invents_an_address():
    assert service_request.store_info(None, None) == {
        "address": "Endereço a confirmar com a assistência.", "hours": "", "configured": ""}
    assert service_request.store_info("Av. Um, 10", "8h às 18h")["configured"] == "1"


async def test_client_requests_service_for_own_equipment():
    gateway = build_demo_gateway(lambda: 2026)
    item = await portal(gateway=gateway).request_service(COURIER)
    order = item.order
    assert order.status == OrderStatus.REQUESTED and order.due_date is None and order.client_id == "1"
    assert (order.delivery_mode, order.pickup_address, order.pickup_period) == (
        DELIVERY_COURIER, "Rua das Flores, 100 - Centro", "Tarde")
    assert order.history[0].description.startswith("Atendimento solicitado pelo cliente (Coleta por motoboy).")
    assert not deadlines.is_overdue(order, AT.date() + timedelta(days=60))  # solicitado não atrasa
    assert (await gateway.orders.get_by_code(order.code)).status == OrderStatus.REQUESTED


async def test_request_is_refused_for_other_clients_equipment_and_for_staff():
    with pytest.raises(ValidationError, match="seus equipamentos"):
        await portal(RAFAEL).request_service(STORE)  # o equipamento 1 é da Marina
    with pytest.raises(PermissionDeniedError):
        await portal(ADMIN).request_service(STORE)


async def test_receiving_a_requested_order():
    gateway = build_demo_gateway(lambda: 2026)
    code = (await portal(gateway=gateway).request_service(STORE)).order.code
    with pytest.raises(PermissionDeniedError):
        await OrderService(gateway, TECH, clock=lambda: AT).change_status(code, "Recebido")
    with pytest.raises(ValidationError, match="Transição não permitida"):
        await OrderService(gateway, ADMIN, clock=lambda: AT).change_status(code, "Em análise")
    received = await OrderService(gateway, ATTENDANT, clock=lambda: AT).change_status(code, "Recebido")
    assert received.status == OrderStatus.RECEIVED and received.due_date == date(2026, 11, 23)


async def test_requests_appear_in_attention_and_not_in_public_progress():
    gateway = build_demo_gateway(lambda: 2026)
    before = await gateway.portal.public_stats()
    code = (await portal(gateway=gateway).request_service(COURIER)).order.code
    assert (await gateway.portal.public_stats()).in_progress == before.in_progress
    data = Catalog(await gateway.clients.list(), await gateway.equipment.list(), await gateway.technicians.list(),
                   await gateway.orders.list())
    row = next(r for r in attention_rows(data, AT.date()) if r["code"] == code)
    assert row["reason"] == "Coleta por motoboy" and row["reason_class"].endswith("requested")


# ----------------------------------------------------------------------
# Equipamentos pelo portal
# ----------------------------------------------------------------------
async def test_client_registers_and_lists_only_own_equipment():
    gateway = build_demo_gateway(lambda: 2026)
    created = await portal(gateway=gateway).add_equipment(
        {"kind": "Notebook", "brand": "Dell", "model": "Inspiron 15", "serial_number": "NOVA-123",
         "client_id": "2"})  # tentativa de cadastrar no cliente 2 é ignorada
    assert created.client_id == "1"
    mine = await portal(gateway=gateway).my_equipment()
    assert created.id in {e.id for e in mine} and all(e.client_id == "1" for e in mine)
    assert created.id not in {e.id for e in await portal(RAFAEL, gateway).my_equipment()}
    with pytest.raises(ValidationError, match="já está cadastrado"):
        await portal(RAFAEL, gateway).add_equipment({"kind": "Notebook", "brand": "Dell", "model": "X",
                                                     "serial_number": "nova-123"})
    with pytest.raises(ValidationError):
        await portal(gateway=gateway).add_equipment({"kind": "Geladeira", "brand": "A", "model": "B"})


# ----------------------------------------------------------------------
# Avisos
# ----------------------------------------------------------------------
def client(email="joana@gmail.com", **changes):
    return Client(id="9", name="Joana Teixeira", cpf="52998224725", email=email, phone="21998765432").model_copy(
        update=changes)


def test_who_can_receive_email():
    assert notifications.can_email(client())
    for email in ("a@exemplo.test", "a@removido.invalid", "a@example.com", "a@loja.example"):
        assert not notifications.can_email(client(email))
    assert not notifications.can_email(client(anonymized=True)) and not notifications.can_email(None)


async def test_message_content_has_no_values_or_diagnosis():
    gateway = build_demo_gateway(lambda: 2026)
    order = await gateway.orders.get_by_code("OS-2026-00123")  # aguardando aprovação, com orçamento
    message = notifications.status_message(order, "Joana Teixeira", "https://site/consulta/OS-2026-00123")
    assert message.subject == "Assistência TECH — OS-2026-00123: Aguardando aprovação"
    assert "Olá, Joana!" in message.text and "aprovar ou recusar" in message.text
    assert "https://site/consulta/OS-2026-00123" in message.text
    assert "R$" not in message.text and order.diagnosis not in message.text and "Teixeira" not in message.text


async def test_requested_message_uses_the_configured_store_address():
    order = (await portal().request_service(STORE)).order
    with_address = notifications.status_message(order, "Marina", store_address="Av. Um, 10", store_hours="8h às 18h")
    assert "Leve o equipamento a: Av. Um, 10. Horário: 8h às 18h." in with_address.text
    assert "vai confirmar o endereço" in notifications.status_message(order, "Marina").text


def test_whatsapp_link():
    link = notifications.whatsapp_link("(21) 99876-5432", "Olá, Joana!")
    assert link == "https://wa.me/5521998765432?text=Ol%C3%A1%2C%20Joana%21"
    assert notifications.whatsapp_link("", "x") == "" and notifications.whatsapp_link("123", "x") == ""


async def test_status_change_emails_the_client(notifier):
    gateway = build_demo_gateway(lambda: 2026)
    marina = await gateway.clients.get("1")
    await gateway.clients.update(marina.model_copy(update={"email": "marina@gmail.com"}))
    await OrderService(gateway, ADMIN, clock=lambda: AT).change_status("OS-2026-00125", "Concluído")
    (to, message), = notifier.sent
    assert to == "marina@gmail.com" and "pronto para retirada" in message.text


async def test_test_addresses_get_no_email(notifier):
    gateway = build_demo_gateway(lambda: 2026)  # marina@example.test
    await OrderService(gateway, ADMIN, clock=lambda: AT).change_status("OS-2026-00125", "Concluído")
    assert notifier.sent == []


async def test_email_failure_does_not_undo_the_operation():
    notify.set_notifier(FakeNotifier(fail=True))
    try:
        gateway = build_demo_gateway(lambda: 2026)
        marina = await gateway.clients.get("1")
        await gateway.clients.update(marina.model_copy(update={"email": "marina@gmail.com"}))
        saved = await OrderService(gateway, ADMIN, clock=lambda: AT).change_status("OS-2026-00125", "Concluído")
    finally:
        notify.set_notifier(None)
    assert saved.status == OrderStatus.DONE


async def test_brevo_request_shape():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(url=str(request.url), key=request.headers.get("api-key"), body=json.loads(request.content))
        return httpx.Response(201, json={"messageId": "x"})

    sender = notify.BrevoNotifier("chave-de-teste", "contato@loja.com.br", transport=httpx.MockTransport(handler))
    assert await sender.send("joana@gmail.com", "Joana", notifications.Message("Assunto", "Texto"))
    assert seen["url"] == "https://api.brevo.com/v3/smtp/email" and seen["key"] == "chave-de-teste"
    assert seen["body"] == {"sender": {"name": "Assistência TECH", "email": "contato@loja.com.br"},
                            "to": [{"email": "joana@gmail.com", "name": "Joana"}],
                            "subject": "Assunto", "textContent": "Texto"}
    refused = notify.BrevoNotifier("k", "a@b.co", transport=httpx.MockTransport(lambda r: httpx.Response(401)))
    assert not await refused.send("joana@gmail.com", "Joana", notifications.Message("A", "T"))


def test_notifier_only_with_xano_and_full_configuration():
    full = {"ASSISTENCIA_DATA_SOURCE": "xano", "XANO_BASE_URL": "https://x.invalid", "BREVO_API_KEY": "segredo-123",
            "ASSISTENCIA_EMAIL_FROM": "contato@loja.com.br", "ASSISTENCIA_STORE_ADDRESS": "Av. Um, 10"}
    settings = load_settings(full)
    assert isinstance(notify.build_notifier(settings), notify.BrevoNotifier)
    assert "segredo-123" not in repr(settings)  # a chave não aparece em logs
    assert isinstance(notify.build_notifier(load_settings({**full, "ASSISTENCIA_DATA_SOURCE": "demo"})),
                      notify.NullNotifier)
    assert isinstance(notify.build_notifier(load_settings({k: v for k, v in full.items() if k != "BREVO_API_KEY"})),
                      notify.NullNotifier)
    with pytest.raises(ConfigurationError):
        load_settings({**full, "ASSISTENCIA_EMAIL_FROM": "sem arroba"})
    assert load_settings({"RENDER_EXTERNAL_URL": "https://site.onrender.com"}).public_url == "https://site.onrender.com"


# ----------------------------------------------------------------------
# Xano
# ----------------------------------------------------------------------
CREATED = int(AT.timestamp() * 1000)
XANO_DEVICE = {"id": 5, "cliente_id": 7, "aparelho": "Notebook", "marca": "Dell", "modelo": "Inspiron",
               "numero_serie": "", "observacoes": ""}
XANO_ORDER = {
    "id": 30, "created_at": CREATED, "atualizado_em": CREATED, "cliente_id": 7, "item_cliente_id": 5, "user_id": None,
    "descricao_problema": "Não liga", "status": "solicitado", "previsao_entrega": None, "entrega_modo": "motoboy",
    "coleta_endereco": "Rua das Flores, 100 - Centro", "coleta_periodo": "Tarde",
    "_itens": [], "_pagamentos": [], "_historico": [], "_aparelho": XANO_DEVICE,
}


def test_xano_mapping_of_requested_order():
    order = mappers.order_from(XANO_ORDER)
    assert order.status == OrderStatus.REQUESTED and order.due_date is None
    assert (order.delivery_mode, order.pickup_period) == (DELIVERY_COURIER, "Tarde")
    assert mappers.order_from({**XANO_ORDER, "status": "recebido", "entrega_modo": None}).delivery_mode == ""


async def test_xano_portal_endpoints_use_the_token_client():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.split("/api:", 1)[1].split("/", 1)[1]
        body = json.loads(request.content) if request.content else None
        calls.append((request.method, path, body))
        if path == "portal/equipamentos":
            return httpx.Response(200, json=[XANO_DEVICE] if request.method == "GET" else XANO_DEVICE)
        if path == "portal/solicitacao":
            return httpx.Response(200, json={k: v for k, v in XANO_ORDER.items() if not k.startswith("_")})
        if path == "portal/minhas_ordens":
            return httpx.Response(200, json=[XANO_ORDER])
        return httpx.Response(404, json={"message": ""})

    http = XanoClient("https://exemplo.invalid", 5, transport=httpx.MockTransport(handler),
                      pacer=RequestPacer(10_000, 1), cache=ResponseCache(0))
    gateway = build_xano_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"), client=http)
    use_backend_token("jwt-cliente")
    try:
        maria = Principal("3", "Maria", "m@x.test", Role.CLIENT, client_id="7")
        service = PortalService(gateway, maria, clock=lambda: AT)
        await service.add_equipment({"kind": "Notebook", "brand": "Dell", "model": "Inspiron"})
        item = await service.request_service({**COURIER, "equipment_id": "5"})
    finally:
        use_backend_token(None)
    assert item.order.code == "OS-2026-00030" and item.order.status == OrderStatus.REQUESTED
    created = next(body for method, path, body in calls if (method, path) == ("POST", "portal/equipamentos"))
    assert "cliente_id" not in created and created["aparelho"] == "Notebook"
    assert ("POST", "portal/solicitacao", {"item_cliente_id": 5, "descricao_problema": "Não liga",
                                          "entrega_modo": "motoboy",
                                          "coleta_endereco": "Rua das Flores, 100 - Centro",
                                          "coleta_periodo": "Tarde"}) in calls
