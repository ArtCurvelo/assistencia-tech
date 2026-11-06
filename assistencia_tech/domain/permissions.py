"""Perfis de acesso, permissões e regras de autorização (funções puras).

``ROLE_PERMISSIONS`` é a matriz da proposta ``add-auth-and-access-control``.
A interface consulta estas funções para exibir ações, e os serviços as
chamam para recusar operações não permitidas.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..data.errors import AuthenticationError, PermissionDeniedError
from ..models.entities import OrderStatus, ServiceOrder
from ..models.users import Role, UserAccount
from .order_workflow import allowed_next

S = OrderStatus


class Permission(StrEnum):
    DASHBOARD_VIEW = "dashboard.view"
    CLIENTS_VIEW = "clients.view"
    CLIENTS_MANAGE = "clients.manage"
    CLIENTS_DELETE = "clients.delete"
    EQUIPMENT_VIEW = "equipment.view"
    EQUIPMENT_MANAGE = "equipment.manage"
    EQUIPMENT_DELETE = "equipment.delete"
    ORDERS_VIEW = "orders.view"
    ORDERS_OPEN = "orders.open"
    ORDERS_ASSIGN = "orders.assign"
    ORDERS_DIAGNOSE = "orders.diagnose"
    ORDERS_STATUS_TECHNICAL = "orders.status.technical"
    ORDERS_APPROVE = "orders.approve"
    ORDERS_PAYMENTS = "orders.payments"
    ORDERS_DELIVER = "orders.deliver"
    ORDERS_CANCEL = "orders.cancel"
    PORTAL_VIEW = "portal.view"


P = Permission

PERMISSION_LABELS: dict[Permission, str] = {
    P.DASHBOARD_VIEW: "acessar o painel administrativo",
    P.CLIENTS_VIEW: "consultar clientes",
    P.CLIENTS_MANAGE: "cadastrar ou editar clientes",
    P.CLIENTS_DELETE: "excluir clientes",
    P.EQUIPMENT_VIEW: "consultar equipamentos",
    P.EQUIPMENT_MANAGE: "cadastrar ou editar equipamentos",
    P.EQUIPMENT_DELETE: "excluir equipamentos",
    P.ORDERS_VIEW: "consultar ordens de serviço",
    P.ORDERS_OPEN: "abrir ordens de serviço",
    P.ORDERS_ASSIGN: "atribuir o técnico responsável",
    P.ORDERS_DIAGNOSE: "registrar diagnóstico e orçamento",
    P.ORDERS_STATUS_TECHNICAL: "alterar o status técnico da ordem",
    P.ORDERS_APPROVE: "registrar a aprovação do orçamento",
    P.ORDERS_PAYMENTS: "registrar pagamentos",
    P.ORDERS_DELIVER: "registrar a entrega",
    P.ORDERS_CANCEL: "cancelar ordens de serviço",
    P.PORTAL_VIEW: "acessar o portal do cliente",
}

_STAFF_VIEW = frozenset({P.DASHBOARD_VIEW, P.CLIENTS_VIEW, P.EQUIPMENT_VIEW, P.ORDERS_VIEW})

ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(set(P) - {P.PORTAL_VIEW}),
    Role.ATTENDANT: _STAFF_VIEW
    | {
        P.CLIENTS_MANAGE,
        P.EQUIPMENT_MANAGE,
        P.ORDERS_OPEN,
        P.ORDERS_ASSIGN,
        P.ORDERS_APPROVE,
        P.ORDERS_PAYMENTS,
        P.ORDERS_DELIVER,
        P.ORDERS_CANCEL,
    },
    Role.TECHNICIAN: _STAFF_VIEW | {P.ORDERS_DIAGNOSE, P.ORDERS_STATUS_TECHNICAL},
    Role.CLIENT: frozenset({P.PORTAL_VIEW}),
}

STAFF_ROLES = frozenset({Role.ADMIN, Role.ATTENDANT, Role.TECHNICIAN})


@dataclass(frozen=True)
class Principal:
    """Usuário autenticado, sem dados sensíveis (nunca contém o hash da senha)."""

    user_id: str
    name: str
    email: str
    role: Role
    client_id: str | None = None
    technician_id: str | None = None

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.role})"

    @property
    def is_staff(self) -> bool:
        return self.role in STAFF_ROLES

    @property
    def home_path(self) -> str:
        return "/admin" if self.is_staff else "/minha-conta"


def permissions_of(principal: Principal | None) -> frozenset[Permission]:
    return ROLE_PERMISSIONS[principal.role] if principal else frozenset()


def has_permission(principal: Principal | None, permission: Permission) -> bool:
    return permission in permissions_of(principal)


def require_principal(principal: Principal | None) -> Principal:
    if principal is None:
        raise AuthenticationError()
    return principal


def require(principal: Principal | None, permission: Permission) -> Principal:
    user = require_principal(principal)
    if permission not in ROLE_PERMISSIONS[user.role]:
        raise PermissionDeniedError(
            f"O perfil {user.role} não tem permissão para {PERMISSION_LABELS[permission]}."
        )
    return user


def status_permission(current: OrderStatus, target: OrderStatus) -> Permission:
    """Permissão necessária para mover a ordem de ``current`` para ``target``."""
    if target == S.CANCELLED:
        return P.ORDERS_CANCEL
    if target == S.DELIVERED:
        return P.ORDERS_DELIVER
    if current == S.AWAITING_APPROVAL and target == S.REPAIR:
        return P.ORDERS_APPROVE
    return P.ORDERS_STATUS_TECHNICAL


def is_own_order(principal: Principal, order: ServiceOrder) -> bool:
    return principal.role != Role.TECHNICIAN or order.technician_id == principal.technician_id


def ensure_can_modify_order(principal: Principal, order: ServiceOrder) -> None:
    """Escopo do técnico: só altera as ordens em que é o responsável."""
    if not is_own_order(principal, order):
        raise PermissionDeniedError("Esta ordem pertence a outro técnico; você pode apenas consultá-la.")


def transitions_for(principal: Principal | None, order: ServiceOrder) -> tuple[OrderStatus, ...]:
    """Próximos status que este usuário pode aplicar à ordem."""
    if principal is None or not is_own_order(principal, order):
        return ()
    return tuple(t for t in allowed_next(order.status) if has_permission(principal, status_permission(order.status, t)))


def principal_from(user: UserAccount) -> Principal:
    return Principal(
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        client_id=user.client_id,
        technician_id=user.technician_id,
    )


def system_principal(name: str = "Sistema") -> Principal:
    """Identidade usada por fluxos automáticos (ex.: autoatendimento do cadastro)."""
    return Principal(user_id="sistema", name=name, email="", role=Role.ADMIN)
