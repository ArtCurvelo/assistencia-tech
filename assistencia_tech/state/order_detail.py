"""Estado da página de detalhe da ordem de serviço."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import reflex as rx

from ..data.errors import DataAccessError, NotFoundError
from ..models import OrderStatus, ServiceOrder
from ..presenters import (
    history_rows,
    item_rows,
    next_statuses,
    order_permissions,
    order_row,
    payment_rows,
    totals_row,
)
from ..services import OrderService, load_catalog
from ..domain.permissions import Permission
from .base import AdminState

CANCELLED = OrderStatus.CANCELLED.value


class OrderDetailState(AdminState):
    found: bool = False
    code: str = ""
    order: dict[str, str] = {}
    diagnosis: str = ""
    cancel_reason: str = ""
    items: list[dict[str, str]] = []
    payments: list[dict[str, str]] = []
    timeline: list[dict[str, str]] = []
    totals: dict[str, str] = {}
    permissions: dict[str, str] = {}
    next_status: list[str] = []
    item_kind: str = "Serviço"
    item_form_key: int = 0
    payment_form_key: int = 0

    cancel_open: bool = False

    async def _show(self, order: ServiceOrder) -> None:
        principal = await self._current()
        catalog = await load_catalog(self._gateway(), principal)
        self.code = order.code
        self.order = order_row(order, catalog)
        self.diagnosis = order.diagnosis
        self.cancel_reason = order.cancel_reason
        self.items = item_rows(order)
        self.payments = payment_rows(order)
        self.timeline = list(reversed(history_rows(order)))
        self.totals = totals_row(order)
        self.permissions = order_permissions(order, principal)
        self.next_status = next_statuses(order, principal)
        self.technicians = [
            {"value": t.id, "label": f"{t.name} — {t.specialty}"} for t in catalog.technicians if t.active
        ]
        self.found = True

    async def load_order(self):
        self._clear_feedback()
        self.found = False
        redirect = await self._guard(Permission.ORDERS_VIEW)
        if redirect is not None:
            return redirect
        code = str(self.router.page.params.get("codigo", ""))
        try:
            order = await OrderService(self._gateway(), await self._current()).get(code)
            await self._show(order)
            self.data_error = ""
        except NotFoundError:
            self.data_error = ""
        except DataAccessError as error:
            self.data_error = error.user_message

    async def _run(
        self,
        action: Callable[[OrderService], Awaitable[ServiceOrder]],
        message: str,
        close_cancel: bool = False,
    ):
        """Executa uma ação sobre a ordem com carregamento e feedback padronizados."""
        if not self._start():
            return
        yield
        try:
            order = await action(OrderService(self._gateway(), await self._current()))
            await self._show(order)
            if close_cancel:
                self.cancel_open = False
            yield self._succeed(message)
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    # Os manipuladores abaixo delegam a ``_run``; cada um é um evento Reflex.
    async def assign_technician(self, technician_id: str):
        async for event in self._run(lambda s: s.assign_technician(self.code, technician_id), "Técnico atualizado."):
            yield event

    async def save_diagnosis(self, form_data: dict):
        text = form_data.get("diagnosis", "")
        async for event in self._run(lambda s: s.record_diagnosis(self.code, text), "Diagnóstico registrado."):
            yield event

    def set_item_kind(self, value: str):
        self.item_kind = value

    async def add_item(self, form_data: dict):
        form = {**form_data, "kind": self.item_kind}
        async for event in self._run(lambda s: s.add_item(self.code, form), "Item adicionado ao orçamento."):
            yield event
        if self.feedback_kind == "success":
            self.item_form_key += 1

    async def remove_item(self, item_id: str):
        async for event in self._run(lambda s: s.remove_item(self.code, item_id), "Item removido do orçamento."):
            yield event

    async def add_payment(self, form_data: dict):
        async for event in self._run(lambda s: s.add_payment(self.code, form_data), "Pagamento registrado."):
            yield event
        if self.feedback_kind == "success":
            self.payment_form_key += 1

    async def change_status(self, status: str):
        if status == CANCELLED:
            self._clear_feedback()
            self.cancel_open = True
            return
        async for event in self._run(lambda s: s.change_status(self.code, status), f"Status alterado para {status}."):
            yield event

    def set_cancel_open(self, value: bool):
        self.cancel_open = value

    async def confirm_cancel(self, form_data: dict):
        reason = form_data.get("reason", "")
        action = lambda s: s.change_status(self.code, CANCELLED, reason)  # noqa: E731
        async for event in self._run(action, "Ordem cancelada.", close_cancel=True):
            yield event
