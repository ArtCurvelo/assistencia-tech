"""Gestão de colaboradores e relatórios (cenários das specs da Fase 5)."""

from datetime import date
from decimal import Decimal

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.demo.auth import DemoAuthProvider
from assistencia_tech.data.demo.users import seed_users
from assistencia_tech.data.errors import AuthenticationError, PermissionDeniedError, ValidationError
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.services import AuthService, OrderService, ReportService, StaffService, reset_auth_state

pytestmark = pytest.mark.anyio

ADMIN = Principal("1", "Ana Ribeiro", "admin@assistencia.test", Role.ADMIN)
ATTENDANT = Principal("2", "Paulo Nunes", "atendimento@assistencia.test", Role.ATTENDANT)
CARLOS = Principal("3", "Carlos Mendes", "carlos@assistencia.test", Role.TECHNICIAN, technician_id="1")
NEW_TECH = {"name": "Bruno Alves", "email": "bruno@assistencia.test", "role": "Técnico",
            "specialty": "Impressoras", "password": "bruno2026"}


@pytest.fixture
def gw():
    gateway = build_demo_gateway(year_provider=lambda: 2026)
    object.__setattr__(gateway, "auth", DemoAuthProvider(seed_users(), iterations=1_000))
    reset_auth_state()
    yield gateway
    reset_auth_state()


@pytest.fixture
def staff(gw):
    return StaffService(gw, ADMIN)


# ------------------------------------------------------------- permissões
async def test_only_admin_manages_staff(gw):
    for principal in (ATTENDANT, CARLOS):
        with pytest.raises(PermissionDeniedError):
            await StaffService(gw, principal).list_staff()
    with pytest.raises(AuthenticationError):
        await StaffService(gw, None).create(NEW_TECH)


async def test_reports_permissions(gw):
    period = ReportService(gw, ADMIN).period("2026-10-01", "2026-10-31")
    await ReportService(gw, ATTENDANT).report(period)
    with pytest.raises(PermissionDeniedError):
        await ReportService(gw, CARLOS).report(period)


# ------------------------------------------------------------------ lista
async def test_list_shows_only_staff(staff):
    members = await staff.list_staff()
    roles = {m.user.role for m in members}
    assert roles == {Role.ADMIN, Role.ATTENDANT, Role.TECHNICIAN}
    assert len(members) == 5
    carlos = next(m for m in members if m.user.name == "Carlos Mendes")
    assert carlos.technician.specialty == "Computadores e notebooks"


# --------------------------------------------------------------- cadastro
async def test_create_technician_can_login_and_be_assigned(gw, staff):
    user = await staff.create(NEW_TECH)
    assert user.role == Role.TECHNICIAN and user.technician_id == "4"
    _, principal = await AuthService(gw).login("bruno@assistencia.test", "bruno2026")
    assert principal.technician_id == "4"
    order = await OrderService(gw, ADMIN).assign_technician("OS-2026-00126", "4")
    assert order.technician_id == "4"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"email": "carlos@assistencia.test"}, "já existe uma conta|Já existe uma conta"),
        ({"password": "123"}, "mínimo 8 caracteres"),
        ({"role": "Cliente"}, "Cargo inválido"),
        ({"specialty": ""}, "especialidade"),
        ({"email": "sem-arroba"}, "e-mail válido"),
    ],
)
async def test_create_rejections(gw, staff, changes, message):
    before = len(await gw.auth.list_users())
    with pytest.raises(ValidationError, match=message):
        await staff.create({**NEW_TECH, **changes})
    assert len(await gw.auth.list_users()) == before


# ---------------------------------------------------------------- edição
async def test_technician_with_open_orders_cannot_change_role(staff):
    with pytest.raises(ValidationError, match="ordens em aberto"):
        await staff.update("3", {"name": "Carlos Mendes", "role": "Atendente"})


async def test_promote_attendant_to_admin_applies_on_next_action(gw, staff):
    token, _ = await AuthService(gw).login("atendimento@assistencia.test", "atende2026")
    await staff.update("2", {"name": "Paulo Nunes", "role": "Administrador"})
    assert (await AuthService(gw).resolve(token)).principal.role == Role.ADMIN


async def test_technician_without_orders_becomes_attendant_and_back(gw, staff):
    user = await staff.create(NEW_TECH)
    await staff.update(user.id, {"name": "Bruno Alves", "role": "Atendente"})
    techs = {t.id: t for t in await gw.technicians.list()}
    assert techs["4"].active is False
    back = await staff.update(user.id, {"name": "Bruno A.", "role": "Técnico", "specialty": "Redes"})
    techs = {t.id: t for t in await gw.technicians.list()}
    assert back.technician_id == "4" and techs["4"].active and techs["4"].name == "Bruno A."


async def test_admin_cannot_demote_self_and_last_admin_protected(staff):
    with pytest.raises(ValidationError, match="próprio cargo"):
        await staff.update("1", {"name": "Ana Ribeiro", "role": "Atendente"})
    other_admin = StaffService(staff._gw, Principal("99", "Outro", "x@x.test", Role.ADMIN))
    with pytest.raises(ValidationError, match="ao menos um administrador"):
        await other_admin.update("1", {"name": "Ana Ribeiro", "role": "Atendente"})
    with pytest.raises(ValidationError, match="ao menos um administrador"):
        await other_admin.set_active("1", False)


# ------------------------------------------------------- ativação e senha
async def test_deactivation_blocks_login_and_session(gw, staff):
    token, _ = await AuthService(gw).login("atendimento@assistencia.test", "atende2026")
    await staff.set_active("2", False)
    assert (await AuthService(gw).resolve(token)).principal is None
    with pytest.raises(AuthenticationError, match="E-mail ou senha inválidos"):
        await AuthService(gw).login("atendimento@assistencia.test", "atende2026")
    await staff.set_active("2", True)
    await AuthService(gw).login("atendimento@assistencia.test", "atende2026")


async def test_cannot_deactivate_self_or_busy_technician(staff):
    with pytest.raises(ValidationError, match="própria conta"):
        await staff.set_active("1", False)
    with pytest.raises(ValidationError, match="ordens em aberto"):
        await staff.set_active("3", False)  # Carlos tem ordens em aberto


async def test_inactive_technician_not_assignable(gw, staff):
    user = await staff.create(NEW_TECH)
    await staff.set_active(user.id, False)
    with pytest.raises(ValidationError, match="inativo"):
        await OrderService(gw, ADMIN).assign_technician("OS-2026-00126", "4")


async def test_reset_password(gw, staff):
    with pytest.raises(ValidationError):
        await staff.reset_password("3", "fraca")
    await staff.reset_password("3", "novaSenha2026")
    await AuthService(gw).login("carlos@assistencia.test", "novaSenha2026")
    with pytest.raises(AuthenticationError):
        await AuthService(gw).login("carlos@assistencia.test", "tecnico2026")


# -------------------------------------------------------------- relatórios
async def test_report_and_csv_through_service(gw):
    service = ReportService(gw, ATTENDANT, today=lambda: date(2026, 11, 6))
    assert service.default_period().start == date(2026, 8, 8)
    period = service.period("2026-10-01", "2026-10-31")
    report = await service.report(period)
    assert report.volume.opened == 7 and report.revenue.total == Decimal("325.00")
    filename, content = await service.export_csv(period)
    assert filename == "ordens-2026-10-01-a-2026-10-31.csv"
    assert content.count("\r\n") == 8


@pytest.mark.parametrize(("start", "end", "message"), [
    ("2026-11-02", "2026-11-01", "Período inválido"),
    ("ontem", "2026-11-01", "datas válidas"),
    ("", "", "datas válidas"),
])
async def test_invalid_periods(gw, start, end, message):
    with pytest.raises(ValidationError, match=message):
        ReportService(gw, ADMIN).period(start, end)
