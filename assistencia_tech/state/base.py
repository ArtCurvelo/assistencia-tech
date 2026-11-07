"""Estado raiz: sessão, fonte de dados ativa, feedback e controle de carregamento.

Os subestados de cada área herdam daqui. O estado não conhece a fonte de
dados nem decide permissões: usa os serviços de aplicação, que verificam
cada operação, e as funções de ``domain.permissions`` para a interface.
"""

from __future__ import annotations

import logging
from urllib.parse import quote

import reflex as rx

from ..data.errors import AuthenticationError, DataAccessError, ServiceUnavailableError
from ..data.factory import get_gateway
from ..data.repositories import DataGateway
from ..domain.permissions import Permission, Principal, has_permission, permissions_of
from ..presenters import (
    EMPTY_METRICS,
    client_row,
    dashboard_metrics,
    equipment_row,
    order_row,
    part_option,
    payment_summary,
    status_chart,
    status_counts,
)
from ..domain.inventory import needs_restock
from ..services import AuthService, InventoryService, load_catalog

logger = logging.getLogger(__name__)

FEEDBACK_SUCCESS = "success"
FEEDBACK_ERROR = "error"
SESSION_COOKIE = "assistencia_sessao"
SESSION_COOKIE_MAX_AGE = 8 * 60 * 60  # o servidor expira antes, após 2 h sem atividade


def safe_next(path: str | None, default: str) -> str:
    """Aceita apenas caminhos internos (evita redirecionamento aberto)."""
    if path and path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return path
    return default


class AppState(rx.State):
    # Token opaco da sessão; os dados da sessão ficam no servidor.
    session_token: str = rx.Cookie("", name=SESSION_COOKIE, same_site="strict", max_age=SESSION_COOKIE_MAX_AGE)

    is_authenticated: bool = False
    user_name: str = ""
    user_role: str = ""
    user_home: str = "/login"
    user_permissions: list[str] = []

    data_source_label: str = ""
    is_demo: bool = True
    data_error: str = ""
    is_loading: bool = False
    feedback_message: str = ""
    feedback_kind: str = ""
    mobile_menu_open: bool = False

    def toggle_mobile_menu(self):
        self.mobile_menu_open = not self.mobile_menu_open

    def close_mobile_menu(self):
        self.mobile_menu_open = False

    # ------------------------------------------------------------------
    # Sessão
    # ------------------------------------------------------------------
    def _gateway(self) -> DataGateway:
        gateway = get_gateway()
        self.data_source_label = gateway.label
        self.is_demo = gateway.is_demo
        return gateway

    def _apply_principal(self, principal: Principal | None) -> None:
        self.is_authenticated = principal is not None
        self.user_name = principal.name if principal else ""
        self.user_role = principal.role.value if principal else ""
        self.user_home = principal.home_path if principal else "/login"
        self.user_permissions = sorted(p.value for p in permissions_of(principal))

    async def _session(self):
        result = await AuthService(self._gateway()).resolve(self.session_token)
        self._apply_principal(result.principal)
        if result.principal is None and self.session_token:
            self.session_token = ""
        return result

    async def _current(self) -> Principal | None:
        try:
            return (await self._session()).principal
        except ServiceUnavailableError:
            # Indisponibilidade não é falta de sessão: o chamador mostra o erro sem deslogar.
            raise
        except DataAccessError:
            self._apply_principal(None)
            return None

    def _login_redirect(self, expired: bool = False):
        target = quote(self.router.page.raw_path or "/admin", safe="/")
        suffix = "&expirada=1" if expired else ""
        return rx.redirect(f"/login?proximo={target}{suffix}")

    async def _guard(self, permission: Permission):
        """Retorna um redirecionamento se o acesso não for permitido; senão ``None``."""
        try:
            result = await self._session()
        except ServiceUnavailableError as error:
            # Backend indisponível ou no limite de requisições: não encerra a sessão.
            self.data_error = error.user_message
            return rx.toast.error(error.user_message)
        except DataAccessError as error:
            self.data_error = error.user_message
            return self._login_redirect()
        if result.principal is None:
            return self._login_redirect(result.expired)
        if not has_permission(result.principal, permission):
            return rx.redirect("/acesso-negado")
        return None

    async def load_session(self):
        """``on_load`` das páginas públicas: só identifica o usuário, sem exigir login."""
        try:
            await self._current()
        except ServiceUnavailableError as error:
            self.data_error = error.user_message

    def logout(self):
        try:
            AuthService(self._gateway()).logout(self.session_token)
        except DataAccessError:
            pass
        self.session_token = ""
        self._apply_principal(None)
        return rx.redirect("/login")

    # ------------------------------------------------------------------
    # Permissões para a interface (os serviços verificam de novo)
    # ------------------------------------------------------------------
    def _can(self, permission: Permission) -> bool:
        return permission.value in self.user_permissions

    @rx.var
    def can_manage_clients(self) -> bool:
        return self._can(Permission.CLIENTS_MANAGE)

    @rx.var
    def can_delete_clients(self) -> bool:
        return self._can(Permission.CLIENTS_DELETE)

    @rx.var
    def can_manage_equipment(self) -> bool:
        return self._can(Permission.EQUIPMENT_MANAGE)

    @rx.var
    def can_delete_equipment(self) -> bool:
        return self._can(Permission.EQUIPMENT_DELETE)

    @rx.var
    def can_open_orders(self) -> bool:
        return self._can(Permission.ORDERS_OPEN)

    @rx.var
    def can_manage_staff(self) -> bool:
        return self._can(Permission.STAFF_MANAGE)

    @rx.var
    def can_view_reports(self) -> bool:
        return self._can(Permission.REPORTS_VIEW)

    @rx.var
    def can_view_stock(self) -> bool:
        return self._can(Permission.STOCK_VIEW)

    @rx.var
    def can_manage_stock(self) -> bool:
        return self._can(Permission.STOCK_MANAGE)

    @rx.var
    def is_staff(self) -> bool:
        return self.is_authenticated and self.user_home == "/admin"

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------
    def _clear_feedback(self) -> None:
        self.feedback_message = ""
        self.feedback_kind = ""

    def _succeed(self, message: str):
        self.feedback_message = message
        self.feedback_kind = FEEDBACK_SUCCESS
        return rx.toast.success(message)

    def _fail(self, error: DataAccessError):
        if error.detail:
            logger.info("Falha de acesso a dados: %s", error.detail)
        self.feedback_message = error.user_message
        self.feedback_kind = FEEDBACK_ERROR
        if isinstance(error, AuthenticationError):
            return [rx.toast.error(error.user_message), self._login_redirect(expired=True)]
        return rx.toast.error(error.user_message)

    def _start(self) -> bool:
        """Marca uma operação em andamento; ``False`` se já houver outra."""
        if self.is_loading:
            return False
        self.is_loading = True
        self._clear_feedback()
        return True

    def clear_feedback(self):
        self._clear_feedback()


class AdminState(AppState):
    """Dados compartilhados pelas páginas administrativas."""

    clients: list[dict[str, str]] = []
    equipment: list[dict[str, str]] = []
    technicians: list[dict[str, str]] = []
    orders: list[dict[str, str]] = []
    metrics: dict[str, str] = EMPTY_METRICS
    status_summary: list[dict[str, str]] = []
    status_data: list[dict] = []
    payment_data: list[dict] = []
    # Estoque (add-parts-inventory): alerta do painel e peças para o orçamento.
    low_stock_count: int = 0
    part_options: list[dict[str, str]] = []

    def _required_permission(self) -> Permission:
        return Permission.DASHBOARD_VIEW

    async def _load_stock_summary(self, principal: Principal | None) -> None:
        if not has_permission(principal, Permission.STOCK_VIEW):
            self.low_stock_count, self.part_options = 0, []
            return
        parts = await InventoryService(self._gateway(), principal).list()
        self.low_stock_count = sum(1 for p in parts if needs_restock(p))
        self.part_options = [part_option(p) for p in parts if p.active and p.quantity > 0]

    async def _reload(self) -> None:
        principal = await self._current()
        catalog = await load_catalog(self._gateway(), principal)
        await self._load_stock_summary(principal)
        self.clients = [client_row(c) for c in catalog.clients]
        self.equipment = [equipment_row(e, catalog) for e in catalog.equipment]
        self.technicians = [
            {"value": t.id, "label": f"{t.name} — {t.specialty}"} for t in catalog.technicians if t.active
        ]
        self.orders = [order_row(o, catalog) for o in catalog.orders]
        self.metrics = dashboard_metrics(catalog)
        self.status_summary = status_counts(catalog)
        self.status_data = status_chart(catalog)
        self.payment_data = payment_summary(catalog)
        self.data_error = ""

    async def load_admin_data(self):
        """``on_load`` das páginas administrativas: verifica o acesso antes de enviar dados."""
        self._clear_feedback()
        redirect = await self._guard(self._required_permission())
        if redirect is not None:
            return redirect
        try:
            await self._reload()
        except DataAccessError as error:
            # Mantém os dados já exibidos; nunca substitui por dados fictícios.
            self.data_error = error.user_message
            if not self.orders:
                self.metrics = EMPTY_METRICS

    @rx.var
    def client_options(self) -> list[dict[str, str]]:
        return [{"value": c["id"], "label": f"{c['name']} · {c['cpf']}"} for c in self.clients]

    @rx.var
    def recent_orders(self) -> list[dict[str, str]]:
        return self.orders[:5]
