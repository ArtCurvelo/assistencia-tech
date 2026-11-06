"""Estado Reflex: orquestra a interface e delega o acesso a dados ao gateway.

O estado não conhece a fonte de dados (demonstração ou Xano); ele depende
apenas das interfaces de ``data.repositories`` obtidas por ``get_gateway``.
"""

from __future__ import annotations

import logging

import reflex as rx

from .data.errors import DataAccessError, NotFoundError
from .data.factory import get_gateway
from .models import ClientCreate, EquipmentCreate, OrderCreate, parse_model

logger = logging.getLogger(__name__)

FEEDBACK_SUCCESS = "success"
FEEDBACK_ERROR = "error"


class AppState(rx.State):
    # Consulta pública de OS
    tracking_code: str = ""
    tracking_message: str = ""
    tracking_kind: str = ""

    # Autenticação (ainda demonstrativa; ver mudança futura de autenticação)
    auth_message: str = ""

    # Filtros
    client_search: str = ""
    order_search: str = ""

    # Dados exibidos (carregados do gateway em on_load)
    clients: list[dict[str, str]] = []
    equipment: list[dict[str, str]] = []
    orders: list[dict[str, str]] = []

    # Fonte de dados e feedback
    data_source_label: str = ""
    is_demo: bool = True
    data_error: str = ""
    is_loading: bool = False
    feedback_message: str = ""
    feedback_kind: str = ""

    # ------------------------------------------------------------------
    # Valores derivados
    # ------------------------------------------------------------------
    @rx.var
    def client_names(self) -> list[str]:
        return [client["name"] for client in self.clients]

    @rx.var
    def open_orders(self) -> int:
        return sum(1 for order in self.orders if order["status"] != "Concluído")

    @rx.var
    def filtered_clients(self) -> list[dict[str, str]]:
        query = self.client_search.lower().strip()
        if not query:
            return self.clients
        return [c for c in self.clients if query in c["name"].lower() or query in c["email"].lower()]

    @rx.var
    def filtered_orders(self) -> list[dict[str, str]]:
        query = self.order_search.lower().strip()
        if not query:
            return self.orders
        return [
            o
            for o in self.orders
            if query in o["code"].lower() or query in o["client"].lower() or query in o["device"].lower()
        ]

    # ------------------------------------------------------------------
    # Auxiliares (métodos com "_" não são manipuladores de evento)
    # ------------------------------------------------------------------
    def _succeed(self, message: str):
        self.feedback_message = message
        self.feedback_kind = FEEDBACK_SUCCESS
        return rx.toast.success(message)

    def _fail(self, error: DataAccessError):
        if error.detail:
            logger.info("Falha de acesso a dados: %s", error.detail)
        self.feedback_message = error.user_message
        self.feedback_kind = FEEDBACK_ERROR
        return rx.toast.error(error.user_message)

    def _start(self) -> bool:
        """Marca uma operação em andamento; ``False`` se já houver outra."""
        if self.is_loading:
            return False
        self.is_loading = True
        self.feedback_message = ""
        self.feedback_kind = ""
        return True

    # ------------------------------------------------------------------
    # Carregamento
    # ------------------------------------------------------------------
    async def load_admin_data(self):
        """Carrega os dados das páginas administrativas a partir do gateway."""
        self.feedback_message = ""
        self.feedback_kind = ""
        try:
            gateway = get_gateway()
        except DataAccessError as error:
            self.data_source_label = "Fonte de dados indisponível"
            self.is_demo = False
            self.data_error = error.user_message
            return
        self.data_source_label = gateway.label
        self.is_demo = gateway.is_demo
        try:
            clients = await gateway.clients.list()
            equipment = await gateway.equipment.list()
            orders = await gateway.orders.list()
        except DataAccessError as error:
            # Mantém os dados já exibidos; nunca substitui por dados fictícios.
            self.data_error = error.user_message
            return
        self.clients = [item.model_dump() for item in clients]
        self.equipment = [item.model_dump() for item in equipment]
        self.orders = [item.model_dump() for item in orders]
        self.data_error = ""

    # ------------------------------------------------------------------
    # Consulta pública de OS
    # ------------------------------------------------------------------
    def set_tracking_code(self, value: str):
        self.tracking_code = value
        self.tracking_message = ""
        self.tracking_kind = ""

    async def lookup_order(self):
        code = self.tracking_code.strip()
        if not code:
            self.tracking_message = "Informe o código da ordem de serviço."
            self.tracking_kind = FEEDBACK_ERROR
            return
        try:
            gateway = get_gateway()
            order = await gateway.orders.get_by_code(code)
        except NotFoundError:
            self.tracking_message = "Código não encontrado. Confira o código informado no atendimento."
            self.tracking_kind = FEEDBACK_ERROR
            return
        except DataAccessError as error:
            self.tracking_message = error.user_message
            self.tracking_kind = FEEDBACK_ERROR
            return
        suffix = " (consulta demonstrativa)" if gateway.is_demo else ""
        self.tracking_message = f"{order.code}: {order.status} — {order.device}{suffix}."
        self.tracking_kind = FEEDBACK_SUCCESS

    # ------------------------------------------------------------------
    # Autenticação demonstrativa (inalterada nesta mudança)
    # ------------------------------------------------------------------
    def demo_login(self, form_data: dict):
        self.auth_message = "Login demonstrativo: autenticação real ainda não está conectada."

    def demo_register(self, form_data: dict):
        self.auth_message = "Cadastro demonstrativo: os dados não foram salvos nem enviados."

    # ------------------------------------------------------------------
    # Filtros
    # ------------------------------------------------------------------
    def set_client_search(self, value: str):
        self.client_search = value

    def set_order_search(self, value: str):
        self.order_search = value

    # ------------------------------------------------------------------
    # Cadastros
    # ------------------------------------------------------------------
    async def add_client(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            created = await get_gateway().clients.create(parse_model(ClientCreate, form_data))
            self.clients = [*self.clients, created.model_dump()]
            yield self._succeed(f"Cliente {created.name} cadastrado com sucesso.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    async def add_equipment(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            created = await get_gateway().equipment.create(parse_model(EquipmentCreate, form_data))
            self.equipment = [*self.equipment, created.model_dump()]
            yield self._succeed(f"Equipamento {created.model} cadastrado para {created.client}.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    async def add_order(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            created = await get_gateway().orders.create(parse_model(OrderCreate, form_data))
            self.orders = [created.model_dump(), *self.orders]
            yield self._succeed(f"Ordem {created.code} aberta com sucesso.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    async def update_order_status(self, code: str, status: str):
        if not self._start():
            return
        yield
        try:
            updated = await get_gateway().orders.update_status(code, status)
            self.orders = [updated.model_dump() if o["code"] == updated.code else o for o in self.orders]
            yield self._succeed(f"{updated.code} atualizada para {updated.status}.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False
