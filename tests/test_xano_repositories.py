"""Repositórios Xano e fluxos dos serviços sobre um servidor simulado.

Os registros seguem os esquemas publicados pelo backend (``docs/XANO_BACKEND_SPEC.md``).
"""

import json
from datetime import datetime
from decimal import Decimal

import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data import errors
from assistencia_tech.data.request_context import take_issued_token, use_backend_token
from assistencia_tech.data.sessions import SessionStore
from assistencia_tech.data.xano import XanoClient, build_xano_gateway
from assistencia_tech.data.xano import mappers
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.login_throttle import LoginThrottle
from assistencia_tech.domain.permissions import Principal
from assistencia_tech.models import OrderStatus, Role
from assistencia_tech.services import AuthService, OrderService, PortalService, StaffService, reset_auth_state

pytestmark = pytest.mark.anyio

BASE = "https://exemplo.invalid"
CREATED = int(datetime(2026, 11, 7, 10, 0, tzinfo=BRT).timestamp() * 1000)
UPDATED = CREATED + 3_600_000

ADMIN = {"id": 1, "name": "Ana Admin", "email": "ana@exemplo.test", "role": "admin", "cliente_id": 0,
         "especialidade": None, "ativo": True}
TECH = {"id": 2, "name": "Carlos", "email": "carlos@exemplo.test", "role": "tecnico", "cliente_id": 0,
        "especialidade": "Notebooks", "ativo": True}
CLIENT_USER = {"id": 3, "name": "Maria", "email": "maria@exemplo.test", "role": "cliente", "cliente_id": 7,
               "especialidade": None, "ativo": True}
CLIENT = {"id": 7, "created_at": CREATED, "Nome": "Maria Souza", "Cpf": "52998224725",
          "email": "maria@exemplo.test", "telefone_Aparelho": "11987654321"}
DEVICE = {"id": 5, "cliente_id": 7, "aparelho": "Notebook", "marca": "Dell", "modelo": "Inspiron",
          "numero_serie": "ABC123", "observacoes": None}
ORDER = {
    "id": 12, "created_at": CREATED, "atualizado_em": UPDATED, "cliente_id": 7, "item_cliente_id": 5, "user_id": 2,
    "descricao_problema": "Não liga", "diagnostico": "Fonte queimada", "motivo_cancelamento": None,
    "status": "em_analise",
    "_itens": [{"id": 40, "os_servicos_id": 12, "tipo": "peca", "descricao": "Fonte", "quantidade": 1,
                "valor_unitario": 150.5}],
    "_pagamentos": [],
    "_historico": [{"id": 90, "os_servicos_id": 12, "created_at": CREATED, "autor": "Ana (Administrador)",
                    "tipo": "Abertura", "descricao": "Ordem aberta", "para_status": ""}],
}


class FakeXano:
    """Servidor simulado: responde por (método, caminho) e registra as chamadas."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        group, _, path = request.url.path.partition("/api:")[2].partition("/")
        body = json.loads(request.content) if request.content else None
        self.calls.append((request.method, group, "/" + path, body, request.headers.get("Authorization"),
                           dict(request.url.params)))
        handler = self.routes.get((request.method, "/" + path))
        if handler is None:
            return httpx.Response(404, json={"code": "ERROR_CODE_NOT_FOUND", "message": ""})
        status, payload = handler(body) if callable(handler) else handler
        return httpx.Response(status, json=payload)

    def paths(self):
        return [(c[0], c[2]) for c in self.calls]


def gateway_for(fake):
    client = XanoClient(BASE, 5, transport=httpx.MockTransport(fake))
    return build_xano_gateway(Settings(data_source="xano", xano_base_url=BASE), client=client)


@pytest.fixture(autouse=True)
def _state():
    reset_auth_state(SessionStore(), LoginThrottle())
    use_backend_token(None)
    take_issued_token()
    yield
    use_backend_token(None)
    reset_auth_state()


def staff(role=Role.ADMIN, user_id="1", technician_id=None):
    return Principal(user_id=user_id, name="Ana", email="ana@exemplo.test", role=role, technician_id=technician_id)


# ----------------------------------------------------------------------
# Mapeamento
# ----------------------------------------------------------------------
def test_order_mapping_and_code():
    order = mappers.order_from(ORDER)
    assert order.code == "OS-2026-00012"
    assert order.status == OrderStatus.ANALYSIS
    assert order.technician_id == "2" and order.equipment_id == "5"
    assert order.items[0].unit_price == Decimal("150.50")
    assert order.opened_at == datetime(2026, 11, 7, 10, 0, tzinfo=BRT)
    assert order.history[0].kind == "Abertura"


def test_order_code_parsing():
    assert mappers.normalize_order_code(" os-2026-12 ") == "OS-2026-00012"
    for invalid in ("", "OS-2026", "12", "OS-2026-00000"):
        with pytest.raises(errors.NotFoundError):
            mappers.parse_order_code(invalid)


def test_user_mapping_links_technician_and_client():
    tech = mappers.user_from(TECH)
    assert tech.role == Role.TECHNICIAN and tech.technician_id == "2" and tech.client_id is None
    client = mappers.user_from(CLIENT_USER)
    assert client.role == Role.CLIENT and client.client_id == "7"
    assert client.password_hash == ""


def test_unknown_device_kind_becomes_other():
    assert mappers.equipment_from({**DEVICE, "aparelho": "Smartwatch"}).kind == "Outro"


# ----------------------------------------------------------------------
# Autenticação e sessão (D12)
# ----------------------------------------------------------------------
async def test_login_keeps_jwt_in_the_server_session():
    fake = FakeXano({
        ("POST", "/auth/login"): (200, {"authToken": "jwt-ana", "user_id": 1}),
        ("GET", "/auth/me"): (200, ADMIN),
    })
    service = AuthService(gateway_for(fake))
    token, principal = await service.login("ana@exemplo.test", "senha-correta")
    assert principal.role == Role.ADMIN
    assert "jwt-ana" not in token  # o navegador recebe só o token opaco
    assert fake.calls[0][4] is None  # login sem Authorization
    assert fake.calls[1][4] == "Bearer jwt-ana"

    use_backend_token(None)  # nova requisição: o JWT vem da sessão
    result = await service.resolve(token)
    assert result.principal.user_id == "1"
    assert fake.calls[-1][4] == "Bearer jwt-ana"


async def test_wrong_password_is_generic():
    body = {"code": "ERROR_CODE_ACCESS_DENIED", "message": "E-mail ou senha inválidos.", "payload": ""}
    fake = FakeXano({("POST", "/auth/login"): (403, body)})
    with pytest.raises(errors.AuthenticationError) as info:
        await AuthService(gateway_for(fake)).login("ana@exemplo.test", "errada")
    assert info.value.user_message == "E-mail ou senha inválidos."


async def test_backend_401_ends_the_session():
    state = {"me": (200, ADMIN)}
    fake = FakeXano({
        ("POST", "/auth/login"): (200, {"authToken": "jwt", "user_id": 1}),
        ("GET", "/auth/me"): lambda body: state["me"],
    })
    service = AuthService(gateway_for(fake))
    token, _ = await service.login("ana@exemplo.test", "senha")
    state["me"] = (401, {"code": "ERROR_CODE_UNAUTHORIZED", "message": "Unauthorized"})
    result = await service.resolve(token)
    assert result.principal is None and result.expired
    assert (await service.resolve(token)).principal is None


async def test_signup_creates_client_and_account_in_one_call():
    fake = FakeXano({
        ("POST", "/auth/signup_cliente"): (200, {"authToken": "jwt-maria", "user_id": 3}),
        ("GET", "/auth/me"): (200, CLIENT_USER),
    })
    form = {"name": "Maria Souza", "cpf": "529.982.247-25", "email": "Maria@Exemplo.test",
            "phone": "(11) 98765-4321", "password": "SenhaForte2026", "password_confirm": "SenhaForte2026"}
    _, principal = await AuthService(gateway_for(fake)).register_client(form)
    assert principal.role == Role.CLIENT and principal.client_id == "7"
    method, _, path, body, auth, _ = fake.calls[0]
    assert (method, path, auth) == ("POST", "/auth/signup_cliente", None)
    assert body == {"Nome": "Maria Souza", "Cpf": "52998224725", "email": "maria@exemplo.test",
                    "telefone_Aparelho": "11987654321", "password": "SenhaForte2026"}


# ----------------------------------------------------------------------
# Clientes, equipamentos e colaboradores
# ----------------------------------------------------------------------
async def test_client_list_follows_pagination():
    pages = {1: {"items": [CLIENT], "nextPage": 2}, 2: {"items": [{**CLIENT, "id": 8}], "nextPage": None}}
    fake = FakeXano({("GET", "/cliente"): None})
    fake.routes[("GET", "/cliente")] = lambda body: (200, pages[int(fake.calls[-1][5]["page"])])
    use_backend_token("jwt")
    clients = await gateway_for(fake).clients.list()
    assert [c.id for c in clients] == ["7", "8"]
    assert fake.calls[0][1] == "assistencia-tech-cliente"


async def test_duplicate_cpf_message_comes_from_the_backend():
    body = {"code": "ERROR_CODE_INPUT_ERROR", "message": "Já existe um cliente com este CPF.", "payload": ""}
    fake = FakeXano({("POST", "/cliente"): (400, body)})
    use_backend_token("jwt")
    gateway = gateway_for(fake)
    from assistencia_tech.models import ClientCreate

    data = ClientCreate(name="Maria", cpf="52998224725", email="m@exemplo.test", phone="11987654321")
    with pytest.raises(errors.ValidationError, match="Já existe um cliente com este CPF"):
        await gateway.clients.create(data)


async def test_non_numeric_ids_are_not_found_without_requests():
    fake = FakeXano({})
    use_backend_token("jwt")
    with pytest.raises(errors.NotFoundError):
        await gateway_for(fake).equipment.get("abc")
    assert fake.calls == []


async def test_staff_technician_is_created_as_an_account():
    created = {**TECH, "id": 9, "name": "Bia", "email": "bia@exemplo.test", "especialidade": "Consoles"}
    fake = FakeXano({("GET", "/usuarios"): (200, [ADMIN]), ("POST", "/usuarios"): (200, created)})
    use_backend_token("jwt")
    form = {"name": "Bia", "email": "bia@exemplo.test", "role": "Técnico", "specialty": "Consoles",
            "password": "SenhaForte2026"}
    user = await StaffService(gateway_for(fake), staff()).create(form)
    assert user.technician_id == "9"
    post = next(c for c in fake.calls if c[0] == "POST")
    assert post[3] == {"name": "Bia", "email": "bia@exemplo.test", "password": "SenhaForte2026",
                       "role": "tecnico", "especialidade": "Consoles"}


# ----------------------------------------------------------------------
# Ordens de serviço (D13)
# ----------------------------------------------------------------------
async def test_get_by_code_checks_the_year():
    fake = FakeXano({("GET", "/os_servicos/12"): (200, ORDER)})
    use_backend_token("jwt")
    gateway = gateway_for(fake)
    assert (await gateway.orders.get_by_code("os-2026-00012")).code == "OS-2026-00012"
    with pytest.raises(errors.NotFoundError):
        await gateway.orders.get_by_code("OS-2025-00012")


async def test_open_order_creates_record_and_history():
    created = {**ORDER, "status": "recebido", "user_id": 0, "diagnostico": None, "_itens": [], "_historico": []}
    fake = FakeXano({
        ("GET", "/cliente/7"): (200, CLIENT),
        ("GET", "/item_cliente/5"): (200, DEVICE),
        ("POST", "/os_servicos"): (200, created),
        ("POST", "/os_historico"): (200, {}),
        ("GET", "/os_servicos/12"): (200, created),
    })
    use_backend_token("jwt")
    order = await OrderService(gateway_for(fake), staff()).open(
        {"client_id": "7", "equipment_id": "5", "problem": "Não liga"}
    )
    assert order.code == "OS-2026-00012"
    post = fake.calls[2]
    assert post[3] == {"cliente_id": 7, "item_cliente_id": 5, "descricao_problema": "Não liga", "status": "recebido"}
    history = fake.calls[3]
    assert history[2] == "/os_historico" and history[3]["os_servicos_id"] == 12


async def test_save_sends_only_the_differences():
    state = {"order": ORDER}
    fake = FakeXano({
        ("GET", "/os_servicos/12"): lambda body: (200, state["order"]),
        ("POST", "/os_itens"): (200, {}),
        ("POST", "/os_historico"): (200, {}),
    })
    use_backend_token("jwt")
    service = OrderService(gateway_for(fake), staff(Role.TECHNICIAN, "2", "2"))
    await service.add_item("OS-2026-00012", {"kind": "Serviço", "description": "Limpeza", "unit_price": "80,00"})
    writes = [c for c in fake.calls if c[0] != "GET"]
    assert [(c[0], c[2]) for c in writes] == [("POST", "/os_itens"), ("POST", "/os_historico")]
    assert writes[0][3] == {"os_servicos_id": 12, "tipo": "servico", "descricao": "Limpeza", "quantidade": 1,
                            "valor_unitario": 80.0}


async def test_status_change_patches_the_order():
    fake = FakeXano({
        ("GET", "/os_servicos/12"): (200, ORDER),
        ("PATCH", "/os_servicos/12"): (200, ORDER),
        ("POST", "/os_historico"): (200, {}),
    })
    use_backend_token("jwt")
    service = OrderService(gateway_for(fake), staff())
    await service.change_status("OS-2026-00012", "Cancelado", "Cliente desistiu")
    patch = next(c for c in fake.calls if c[0] == "PATCH")
    assert patch[3] == {"status": "cancelado", "motivo_cancelamento": "Cliente desistiu"}


async def test_removing_an_item_deletes_it():
    fake = FakeXano({
        ("GET", "/os_servicos/12"): (200, ORDER),
        ("DELETE", "/os_itens/40"): (200, {"success": True}),
        ("POST", "/os_historico"): (200, {}),
    })
    use_backend_token("jwt")
    await OrderService(gateway_for(fake), staff()).remove_item("OS-2026-00012", "40")
    assert ("DELETE", "/os_itens/40") in fake.paths()


# ----------------------------------------------------------------------
# Consulta pública e portal (D14)
# ----------------------------------------------------------------------
async def test_public_lookup_needs_no_token_and_hides_personal_data():
    public = {"id": 12, "created_at": CREATED, "status": "em_reparo", "atualizado_em": UPDATED,
              "aparelho": "Notebook", "modelo": "Inspiron"}
    fake = FakeXano({("GET", "/consulta_publica/12"): (200, public)})
    view = await OrderService(gateway_for(fake), None).public_view("OS-2026-00012")
    assert view.status == "Em reparo" and view.equipment == "Notebook Inspiron"
    assert fake.calls[0][4] is None
    with pytest.raises(errors.NotFoundError):
        await OrderService(gateway_for(fake), None).public_view("OS-2025-00012")


async def test_portal_uses_server_side_projections():
    fake = FakeXano({
        ("GET", "/portal/minha_conta"): (200, CLIENT),
        ("GET", "/portal/minhas_ordens"): (200, [{**ORDER, "_aparelho": DEVICE}]),
    })
    use_backend_token("jwt-maria")
    principal = Principal(user_id="3", name="Maria", email="maria@exemplo.test", role=Role.CLIENT, client_id="7")
    service = PortalService(gateway_for(fake), principal)
    assert (await service.account()).name == "Maria Souza"
    orders = await service.my_orders()
    assert orders[0].order.code == "OS-2026-00012" and orders[0].equipment.brand == "Dell"
    assert {c[2] for c in fake.calls} == {"/portal/minha_conta", "/portal/minhas_ordens"}
    with pytest.raises(errors.NotFoundError):
        await service.my_order("OS-2026-00099")
