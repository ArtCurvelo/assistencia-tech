"""Estados das páginas públicas: consulta de OS e autenticação demonstrativa."""

from __future__ import annotations

from ..data.errors import DataAccessError, NotFoundError
from ..domain.clock import format_datetime
from ..services import OrderService
from .base import FEEDBACK_ERROR, FEEDBACK_SUCCESS, AppState


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
            view = await OrderService(gateway).public_view(self.tracking_code)
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
        }
        self.has_result = True
        self.tracking_message = "Consulta demonstrativa." if gateway.is_demo else ""
        self.tracking_kind = FEEDBACK_SUCCESS


class AuthState(AppState):
    """Autenticação ainda demonstrativa (mudança própria de autenticação)."""

    auth_message: str = ""

    def demo_login(self, form_data: dict):
        self.auth_message = "Login demonstrativo: autenticação real ainda não está conectada."

    def demo_register(self, form_data: dict):
        self.auth_message = "Cadastro demonstrativo: os dados não foram salvos nem enviados."
