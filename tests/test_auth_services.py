"""Autenticação, sessões, autorização nos serviços e portal (cenários das specs)."""

from datetime import datetime, timedelta

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.demo.auth import DemoAuthProvider
from assistencia_tech.data.demo.users import DEMO_ACCOUNTS, DEMO_PASSWORDS, seed_users
from assistencia_tech.data.errors import (
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from assistencia_tech.data.sessions import SessionStore
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.login_throttle import LoginThrottle
from assistencia_tech.domain.passwords import verify_password
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import OrderStatus
from assistencia_tech.services import (
    AuthService,
    ClientService,
    EquipmentService,
    OrderService,
    PortalService,
    load_catalog,
    reset_auth_state,
)

pytestmark = pytest.mark.anyio

ADMIN = Principal("1", "Ana Ribeiro", "admin@assistencia.test", Role.ADMIN)
ATTENDANT = Principal("2", "Paulo Nunes", "atendimento@assistencia.test", Role.ATTENDANT)
CARLOS = Principal("3", "Carlos Mendes", "carlos@assistencia.test", Role.TECHNICIAN, technician_id="1")
FERNANDA = Principal("4", "Fernanda Rocha", "fernanda@assistencia.test", Role.TECHNICIAN, technician_id="2")
MARINA = Principal("6", "Marina Oliveira", "marina@example.test", Role.CLIENT, client_id="1")
NEW_CLIENT = {"name": "Ana Costa", "cpf": "52998224725", "email": "ana@exemplo.test", "phone": "11987654321",
              "password": "senha2026", "password_confirm": "senha2026"}


class FakeClock:
    def __init__(self):
        self.now = datetime(2026, 11, 6, 10, 0, tzinfo=BRT)

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def gw(clock):
    gateway = build_demo_gateway(year_provider=lambda: 2026)
    # Iterações reduzidas para novos cadastros nos testes; contas do seed mantêm 600.000.
    object.__setattr__(gateway, "auth", DemoAuthProvider(seed_users(), iterations=1_000))
    reset_auth_state(SessionStore(clock), LoginThrottle(clock))
    yield gateway
    reset_auth_state()


@pytest.fixture
def auth(gw):
    return AuthService(gw)


# ------------------------------------------------------------ demonstração
def test_demo_accounts_cover_every_role_and_passwords_match():
    users = {u.email: u for u in seed_users()}
    assert {users[a.email].role for a in DEMO_ACCOUNTS} == set(Role)
    for email, password in DEMO_PASSWORDS.items():
        assert verify_password(password, users[email].password_hash), email
    assert all(password not in repr(users[email]) for email, password in DEMO_PASSWORDS.items())


# ------------------------------------------------------------------ login
async def test_login_success_and_session(auth):
    token, principal = await auth.login(" ATENDIMENTO@assistencia.test ", "atende2026")
    assert principal.role == Role.ATTENDANT and principal.home_path == "/admin"
    assert len(token) >= 40
    assert (await auth.resolve(token)).principal == principal


async def test_generic_message_for_wrong_password_and_unknown_email(auth):
    with pytest.raises(AuthenticationError) as wrong:
        await auth.login("admin@assistencia.test", "errada123")
    with pytest.raises(AuthenticationError) as unknown:
        await auth.login("ninguem@assistencia.test", "errada123")
    assert wrong.value.user_message == unknown.value.user_message == "E-mail ou senha inválidos."


async def test_lockout_after_five_failures(auth, clock):
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            await auth.login("marina@example.test", "errada123")
    with pytest.raises(AuthenticationError, match="temporariamente bloqueado.*5 minuto"):
        await auth.login("marina@example.test", "cliente2026")
    clock.now += timedelta(minutes=5)
    _, principal = await auth.login("marina@example.test", "cliente2026")
    assert principal.client_id == "1"


async def test_empty_credentials(auth):
    with pytest.raises(ValidationError):
        await auth.login("", "")


async def test_session_expires_after_idle_timeout(auth, clock):
    token, _ = await auth.login("admin@assistencia.test", "admin2026")
    clock.now += timedelta(hours=1, minutes=59)
    assert (await auth.resolve(token)).principal is not None
    clock.now += timedelta(hours=2, seconds=1)
    result = await auth.resolve(token)
    assert result.principal is None and result.expired
    assert (await auth.resolve(token)).expired is False  # já descartada


async def test_unknown_token_and_logout(auth):
    assert (await auth.resolve("token-inventado")).principal is None
    token, _ = await auth.login("admin@assistencia.test", "admin2026")
    auth.logout(token)
    assert (await auth.resolve(token)).principal is None


# --------------------------------------------------------------- cadastro
async def test_register_client_creates_client_and_account(gw, auth):
    token, principal = await auth.register_client(NEW_CLIENT)
    assert principal.role == Role.CLIENT and principal.home_path == "/minha-conta"
    client = await ClientService(gw, ADMIN).get(principal.client_id)
    assert client.name == "Ana Costa"
    assert (await auth.resolve(token)).principal == principal
    _, again = await auth.login("ana@exemplo.test", "senha2026")
    assert again.user_id == principal.user_id


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"password_confirm": "outra2026"}, "não conferem"),
        ({"password": "12345678", "password_confirm": "12345678"}, "mínimo 8 caracteres"),
        ({"email": "admin@assistencia.test"}, "conta com o e-mail"),
        ({"cpf": "39053344705", "email": "nova@exemplo.test"}, "CPF"),
        ({"cpf": "123"}, "CPF"),
    ],
)
async def test_register_rejections_create_nothing(gw, auth, changes, message):
    before = len(await gw.clients.list())
    with pytest.raises(ValidationError, match=message):
        await auth.register_client({**NEW_CLIENT, **changes})
    assert len(await gw.clients.list()) == before


# ------------------------------------------------------------ autorização
async def test_attendant_cannot_delete_client(gw):
    with pytest.raises(PermissionDeniedError, match="Atendente"):
        await ClientService(gw, ATTENDANT).delete("6")
    assert len(await gw.clients.list()) == 6


async def test_technician_cannot_create_client_or_pay(gw):
    with pytest.raises(PermissionDeniedError):
        await ClientService(gw, CARLOS).create({"name": "X", "cpf": "52998224725", "email": "x@x.test",
                                                "phone": "11987654321"})
    with pytest.raises(PermissionDeniedError):
        await OrderService(gw, CARLOS).add_payment("OS-2026-00125", {"amount": "10", "method": "PIX"})
    assert len(await gw.clients.list()) == 6


async def test_no_session_is_rejected(gw):
    for call in (ClientService(gw, None).list(), EquipmentService(gw, None).list(),
                 OrderService(gw, None).list(), load_catalog(gw, None)):
        with pytest.raises(AuthenticationError):
            await call


async def test_client_cannot_use_admin_services(gw):
    with pytest.raises(PermissionDeniedError):
        await ClientService(gw, MARINA).list()
    with pytest.raises(PermissionDeniedError):
        await load_catalog(gw, MARINA)


async def test_technician_scope(gw):
    # OS-2026-00125 é do Carlos; OS-2026-00124 é da Fernanda.
    order = await OrderService(gw, CARLOS).record_diagnosis("OS-2026-00125", "Cooler substituído.")
    assert order.history[-1].author == "Carlos Mendes (Técnico)"
    with pytest.raises(PermissionDeniedError, match="outro técnico"):
        await OrderService(gw, CARLOS).record_diagnosis("OS-2026-00124", "Teste")
    with pytest.raises(PermissionDeniedError, match="outro técnico"):
        await OrderService(gw, CARLOS).add_item("OS-2026-00124", {"kind": "Serviço", "description": "x",
                                                                   "unit_price": "10"})
    await OrderService(gw, FERNANDA).record_diagnosis("OS-2026-00124", "Fonte com defeito.")


async def test_status_permissions_in_service(gw):
    # Atendente registra aprovação; técnico não pode entregar nem aprovar.
    updated = await OrderService(gw, ATTENDANT).change_status("OS-2026-00123", "Em reparo")
    assert updated.status == OrderStatus.REPAIR
    assert updated.history[-1].author == "Paulo Nunes (Atendente)"
    with pytest.raises(PermissionDeniedError):
        await OrderService(gw, CARLOS).change_status("OS-2026-00122", "Entregue")
    with pytest.raises(PermissionDeniedError):
        await OrderService(gw, ATTENDANT).change_status("OS-2026-00125", "Concluído")
    done = await OrderService(gw, CARLOS).change_status("OS-2026-00125", "Concluído")
    assert done.status == OrderStatus.DONE


async def test_technician_cannot_assign(gw):
    with pytest.raises(PermissionDeniedError):
        await OrderService(gw, CARLOS).assign_technician("OS-2026-00126", "1")


async def test_public_view_needs_no_session(gw):
    view = await OrderService(gw, None).public_view("OS-2026-00125")
    assert view.status == "Em reparo"


# ------------------------------------------------------------------ portal
async def test_portal_lists_only_own_orders(gw):
    orders = await PortalService(gw, MARINA).my_orders()
    assert [p.order.code for p in orders] == ["OS-2026-00125"]
    assert (await PortalService(gw, MARINA).account()).name == "Marina Oliveira"


async def test_portal_hides_other_clients_orders(gw):
    with pytest.raises(NotFoundError) as other:
        await PortalService(gw, MARINA).my_order("OS-2026-00124")
    with pytest.raises(NotFoundError) as missing:
        await PortalService(gw, MARINA).my_order("OS-1999-00001")
    assert other.value.user_message == missing.value.user_message
    own = await PortalService(gw, MARINA).my_order("os-2026-00125")
    assert own.equipment.model == "IdeaPad 3"


async def test_staff_cannot_use_portal(gw):
    with pytest.raises(PermissionDeniedError):
        await PortalService(gw, ADMIN).my_orders()
