"""Estado raiz: fonte de dados ativa, feedback e controle de carregamento.

Os subestados de cada área herdam daqui. O estado não conhece a fonte de
dados; ele usa os serviços de aplicação sobre o gateway de ``get_gateway``.
"""

from __future__ import annotations

import logging

import reflex as rx

from ..data.errors import DataAccessError
from ..data.factory import get_gateway
from ..data.repositories import DataGateway
from ..presenters import client_row, dashboard_metrics, equipment_row, order_row, status_counts
from ..services import load_catalog

logger = logging.getLogger(__name__)

FEEDBACK_SUCCESS = "success"
FEEDBACK_ERROR = "error"


class AppState(rx.State):
    data_source_label: str = ""
    is_demo: bool = True
    data_error: str = ""
    is_loading: bool = False
    feedback_message: str = ""
    feedback_kind: str = ""

    # ------------------------------------------------------------------
    # Auxiliares (métodos com "_" não são manipuladores de evento)
    # ------------------------------------------------------------------
    def _gateway(self) -> DataGateway:
        gateway = get_gateway()
        self.data_source_label = gateway.label
        self.is_demo = gateway.is_demo
        return gateway

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
    metrics: dict[str, str] = {}
    status_summary: list[dict[str, str]] = []

    async def _reload(self) -> None:
        catalog = await load_catalog(self._gateway())
        self.clients = [client_row(c) for c in catalog.clients]
        self.equipment = [equipment_row(e, catalog) for e in catalog.equipment]
        self.technicians = [{"value": t.id, "label": f"{t.name} — {t.specialty}"} for t in catalog.technicians]
        self.orders = [order_row(o, catalog) for o in catalog.orders]
        self.metrics = dashboard_metrics(catalog)
        self.status_summary = status_counts(catalog)
        self.data_error = ""

    async def load_admin_data(self):
        """``on_load`` das páginas administrativas."""
        self._clear_feedback()
        try:
            await self._reload()
        except DataAccessError as error:
            if not self.data_source_label:
                self.data_source_label = "Fonte de dados indisponível"
                self.is_demo = False
            # Mantém os dados já exibidos; nunca substitui por dados fictícios.
            self.data_error = error.user_message

    @rx.var
    def client_options(self) -> list[dict[str, str]]:
        return [{"value": c["id"], "label": f"{c['name']} · {c['cpf']}"} for c in self.clients]

    @rx.var
    def recent_orders(self) -> list[dict[str, str]]:
        return self.orders[:5]
