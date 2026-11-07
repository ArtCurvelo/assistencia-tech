"""Estados das páginas públicas: consulta de OS, login e cadastro."""

from __future__ import annotations

import reflex as rx

from ..data.demo.users import DEMO_ACCOUNTS, DEMO_PASSWORDS
from ..data.errors import DataAccessError, NotFoundError
from ..domain.clock import format_datetime
from ..services import AuthService, OrderService
from .base import FEEDBACK_ERROR, FEEDBACK_SUCCESS, AppState, safe_next


class TrackingState(AppState):
    tracking_code: str = ""
    tracking_message: str = ""
    tracking_kind: str = ""
    result: dict[str, str] = {}
    has_result: bool = False

    def set_tracking_code(self, value: str):
        self.tracking_code = value
        self.tracking_message = ""
        self.tracking_kind = ""
        self.result = {}
        self.has_result = False

    async def lookup_order(self):
        self.result = {}
        self.has_result = False
        try:
            gateway = self._gateway()
            view = await OrderService(gateway, None).public_view(self.tracking_code)
        except NotFoundError:
            self.tracking_message = "Código não encontrado. Confira o código informado no atendimento."
            self.tracking_kind = FEEDBACK_ERROR
            return
        except DataAccessError as error:
            self.tracking_message = error.user_message
            self.tracking_kind = FEEDBACK_ERROR
            return
        # Somente a projeção pública chega à página (sem dados pessoais ou valores).
        self.result = {
            "code": view.code,
            "status": view.status,
            "equipment": view.equipment,
            "updated_at": format_datetime(view.updated_at),
            "due_date": f"{view.due_date:%d/%m/%Y}" if view.due_date else "",
        }
        self.has_result = True
        self.tracking_message = "Consulta demonstrativa." if gateway.is_demo else ""
        self.tracking_kind = FEEDBACK_SUCCESS


class LoginState(AppState):
    login_notice: str = ""
    next_path: str = ""

    @rx.var
    def demo_accounts(self) -> list[dict[str, str]]:
        # Somente rótulos e e-mails; as senhas nunca são enviadas ao navegador.
        return [{"key": a.key, "label": a.label, "description": a.description, "email": a.email}
                for a in DEMO_ACCOUNTS]

    async def load_login(self):
        self._clear_feedback()
        params = self.router.page.params
        self.next_path = str(params.get("proximo", ""))
        self.login_notice = (
            "Sua sessão expirou por inatividade. Entre novamente." if params.get("expirada") else ""
        )
        principal = await self._current()
        if principal is not None:
            return rx.redirect(principal.home_path)

    async def _sign_in(self, email: str, password: str):
        token, principal = await AuthService(self._gateway()).login(email, password)
        self.session_token = token
        self._apply_principal(principal)
        default = principal.home_path
        target = safe_next(self.next_path, default)
        # Clientes não entram na área administrativa (e vice-versa).
        if principal.is_staff != target.startswith("/admin"):
            target = default
        return rx.redirect(target)

    def _fail_login(self, error: DataAccessError):
        self.feedback_message = error.user_message
        self.feedback_kind = FEEDBACK_ERROR
        return rx.toast.error(error.user_message)

    async def login(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            yield await self._sign_in(form_data.get("email", ""), form_data.get("password", ""))
        except DataAccessError as error:
            yield self._fail_login(error)
        finally:
            self.is_loading = False

    async def quick_login(self, key: str):
        """Acesso rápido do modo demonstração (a senha de teste é lida no servidor)."""
        if not self._gateway().is_demo:
            return
        account = next((a for a in DEMO_ACCOUNTS if a.key == key), None)
        if account is None or not self._start():
            return
        yield
        try:
            yield await self._sign_in(account.email, DEMO_PASSWORDS[account.email])
        except DataAccessError as error:
            yield self._fail_login(error)
        finally:
            self.is_loading = False


class RegisterState(AppState):
    async def load_register(self):
        self._clear_feedback()
        principal = await self._current()
        if principal is not None:
            return rx.redirect(principal.home_path)

    async def register(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            token, principal = await AuthService(self._gateway()).register_client(form_data)
            self.session_token = token
            self._apply_principal(principal)
            yield rx.toast.success(f"Bem-vindo, {principal.name}! Sua conta foi criada.")
            yield rx.redirect("/minha-conta")
        except DataAccessError as error:
            self.feedback_message = error.user_message
            self.feedback_kind = FEEDBACK_ERROR
            yield rx.toast.error(error.user_message)
        finally:
            self.is_loading = False
