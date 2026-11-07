from datetime import datetime, timedelta

import pytest

from assistencia_tech.data.errors import AuthenticationError, PermissionDeniedError, ValidationError
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.login_throttle import LoginThrottle
from assistencia_tech.domain.passwords import check_password_policy, hash_password, verify_password
from assistencia_tech.domain.permissions import (
    ROLE_PERMISSIONS,
    Permission as P,
    Principal,
    Role,
    ensure_can_modify_order,
    has_permission,
    require,
    status_permission,
    transitions_for,
)
from assistencia_tech.models import OrderStatus as S
from assistencia_tech.models import ServiceOrder

FAST = 1_000  # iterações reduzidas apenas nos testes


# ------------------------------------------------------------------ senhas
def test_same_password_produces_different_hashes():
    first, second = hash_password("segredo123", iterations=FAST), hash_password("segredo123", iterations=FAST)
    assert first != second
    assert "segredo123" not in first
    assert first.startswith(f"pbkdf2_sha256${FAST}$")


def test_verify_password():
    stored = hash_password("segredo123", iterations=FAST)
    assert verify_password("segredo123", stored)
    assert not verify_password("Segredo123", stored)
    assert not verify_password("segredo123", "texto-qualquer")
    assert not verify_password("segredo123", "md5$1$00$00")


def test_default_iterations_follow_owasp():
    assert hash_password("x1x1x1x1", salt=b"0" * 16).split("$")[1] == "600000"


@pytest.mark.parametrize("password", ["12345678", "abcdefgh", "abc123", ""])
def test_weak_passwords_rejected(password):
    with pytest.raises(ValidationError, match="mínimo 8 caracteres"):
        check_password_policy(password)


def test_strong_password_accepted():
    check_password_policy("cliente2026")


# --------------------------------------------------------------- limitador
class FakeClock:
    def __init__(self):
        self.now = datetime(2026, 11, 6, 10, 0, tzinfo=BRT)

    def __call__(self):
        return self.now

    def advance(self, **kwargs):
        self.now += timedelta(**kwargs)


def test_lock_after_five_failures_and_unlock_after_five_minutes():
    clock = FakeClock()
    throttle = LoginThrottle(clock)
    for _ in range(4):
        throttle.register_failure("Ana@Exemplo.test")
    assert throttle.remaining_lock("ana@exemplo.test") is None
    throttle.register_failure("ana@exemplo.test")
    assert throttle.remaining_minutes("ANA@exemplo.test") == 5
    clock.advance(minutes=4, seconds=59)
    assert throttle.remaining_lock("ana@exemplo.test") is not None
    clock.advance(seconds=1)
    assert throttle.remaining_lock("ana@exemplo.test") is None


def test_failures_outside_window_do_not_count():
    clock = FakeClock()
    throttle = LoginThrottle(clock)
    for _ in range(4):
        throttle.register_failure("a@b.test")
    clock.advance(minutes=16)
    throttle.register_failure("a@b.test")
    assert throttle.remaining_lock("a@b.test") is None


def test_success_resets_failures():
    throttle = LoginThrottle(FakeClock())
    for _ in range(4):
        throttle.register_failure("a@b.test")
    throttle.register_success("a@b.test")
    throttle.register_failure("a@b.test")
    assert throttle.remaining_lock("a@b.test") is None


# -------------------------------------------------------------- permissões
ADMIN = Principal("1", "Ana", "a@x.test", Role.ADMIN)
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)
TECH = Principal("3", "Carlos", "c@x.test", Role.TECHNICIAN, technician_id="1")
CLIENT = Principal("4", "Marina", "m@x.test", Role.CLIENT, client_id="1")

# Matriz da proposta: perfil -> permissões esperadas
EXPECTED = {
    Role.ADMIN: set(P) - {P.PORTAL_VIEW, P.PORTAL_DECIDE_BUDGET},
    Role.ATTENDANT: {
        P.DASHBOARD_VIEW, P.CLIENTS_VIEW, P.EQUIPMENT_VIEW, P.ORDERS_VIEW, P.CLIENTS_MANAGE, P.EQUIPMENT_MANAGE,
        P.ORDERS_OPEN, P.ORDERS_ASSIGN, P.ORDERS_APPROVE, P.ORDERS_PAYMENTS, P.ORDERS_DELIVER, P.ORDERS_CANCEL,
        P.REPORTS_VIEW,
    },
    Role.TECHNICIAN: {
        P.DASHBOARD_VIEW, P.CLIENTS_VIEW, P.EQUIPMENT_VIEW, P.ORDERS_VIEW, P.ORDERS_DIAGNOSE,
        P.ORDERS_STATUS_TECHNICAL,
    },
    Role.CLIENT: {P.PORTAL_VIEW, P.PORTAL_DECIDE_BUDGET},  # add-client-budget-approval
}


@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize("permission", list(P))
def test_permission_matrix(role, permission):
    assert (permission in ROLE_PERMISSIONS[role]) == (permission in EXPECTED[role])


def test_only_admin_deletes():
    assert [r for r in Role if P.CLIENTS_DELETE in ROLE_PERMISSIONS[r]] == [Role.ADMIN]
    assert [r for r in Role if P.EQUIPMENT_DELETE in ROLE_PERMISSIONS[r]] == [Role.ADMIN]


def test_require_messages():
    with pytest.raises(AuthenticationError):
        require(None, P.CLIENTS_VIEW)
    with pytest.raises(PermissionDeniedError, match="O perfil Atendente não tem permissão para excluir clientes"):
        require(ATTENDANT, P.CLIENTS_DELETE)
    assert require(ADMIN, P.CLIENTS_DELETE) is ADMIN
    assert not has_permission(None, P.ORDERS_VIEW)


@pytest.mark.parametrize(
    ("current", "target", "permission"),
    [
        (S.RECEIVED, S.ANALYSIS, P.ORDERS_STATUS_TECHNICAL),
        (S.ANALYSIS, S.AWAITING_APPROVAL, P.ORDERS_STATUS_TECHNICAL),
        (S.AWAITING_APPROVAL, S.REPAIR, P.ORDERS_APPROVE),
        (S.REPAIR, S.DONE, P.ORDERS_STATUS_TECHNICAL),
        (S.DONE, S.DELIVERED, P.ORDERS_DELIVER),
        (S.CANCELLED, S.DELIVERED, P.ORDERS_DELIVER),
        (S.REPAIR, S.CANCELLED, P.ORDERS_CANCEL),
    ],
)
def test_status_permissions(current, target, permission):
    assert status_permission(current, target) == permission


def _order(status, technician_id="1"):
    at = datetime(2026, 11, 6, tzinfo=BRT)
    return ServiceOrder(code="OS-2026-00001", client_id="1", equipment_id="1", problem="x", status=status,
                        opened_at=at, updated_at=at, technician_id=technician_id)


def test_technician_scope():
    ensure_can_modify_order(TECH, _order(S.ANALYSIS, "1"))
    with pytest.raises(PermissionDeniedError, match="outro técnico"):
        ensure_can_modify_order(TECH, _order(S.ANALYSIS, "2"))
    ensure_can_modify_order(ATTENDANT, _order(S.ANALYSIS, "2"))


def test_transitions_filtered_by_role_and_scope():
    assert transitions_for(TECH, _order(S.RECEIVED)) == (S.ANALYSIS,)
    assert transitions_for(TECH, _order(S.RECEIVED, "2")) == ()
    assert transitions_for(ATTENDANT, _order(S.RECEIVED)) == (S.CANCELLED,)
    assert transitions_for(ATTENDANT, _order(S.AWAITING_APPROVAL)) == (S.REPAIR, S.CANCELLED)
    assert transitions_for(TECH, _order(S.DONE)) == ()
    assert transitions_for(ADMIN, _order(S.REPAIR)) == (S.DONE, S.CANCELLED)
    assert transitions_for(CLIENT, _order(S.REPAIR)) == ()
    assert transitions_for(None, _order(S.REPAIR)) == ()


def test_principal_helpers():
    assert TECH.display_name == "Carlos (Técnico)"
    assert ADMIN.home_path == "/admin" and CLIENT.home_path == "/minha-conta"
    assert not CLIENT.is_staff


def test_admin_only_permissions():
    assert [r for r in Role if P.STAFF_MANAGE in ROLE_PERMISSIONS[r]] == [Role.ADMIN]
    assert {r for r in Role if P.REPORTS_VIEW in ROLE_PERMISSIONS[r]} == {Role.ADMIN, Role.ATTENDANT}
