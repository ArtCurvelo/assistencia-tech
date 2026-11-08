"""Estados do comprovante da ordem (add-order-receipt) e da consulta pública por link."""

from __future__ import annotations

import reflex as rx

from ..config import load_settings
from ..data.errors import DataAccessError, NotFoundError
from ..domain import receipt
from ..domain.permissions import Permission
from ..models import Client, Equipment, ServiceOrder
from ..presenters import item_rows, payment_rows, receipt_row, totals_row
from ..services import OrderService, PortalService
from .base import FEEDBACK_ERROR, AppState
from .portal import PortalState
from .public import TrackingState

NOT_FOUND = "Código não encontrado. Confira o código informado no atendimento."


def _show_receipt(state: rx.State, order: ServiceOrder, client: Client | None, equipment: Equipment | None) -> None:
    base = receipt.public_base_url(load_settings().public_url, state.router.page.host)
    state.receipt = receipt_row(order, client, equipment, base)
    state.items = item_rows(order)
    state.payments = payment_rows(order)
    state.totals = totals_row(order)
    state.found = True
    state.data_error = ""


class ReceiptState(AppState):
    """Comprovante emitido pela equipe (permissão de consultar ordens)."""

    found: bool = False
    back_href: str = "/admin/ordens"
    receipt: dict[str, str] = {}
    items: list[dict[str, str]] = []
    payments: list[dict[str, str]] = []
    totals: dict[str, str] = {}

    async def load_receipt(self):
        self.found = False
        redirect = await self._guard(Permission.ORDERS_VIEW)
        if redirect is not None:
            return redirect
        code = str(self.router.page.params.get("codigo", ""))
        self.back_href = "/admin/ordens/" + code
        try:
            order, client, equipment = await OrderService(self._gateway(), await self._current()).receipt(code)
        except NotFoundError:
            self.data_error = ""
            return
        except DataAccessError as error:
            self.data_error = error.user_message
            return
        _show_receipt(self, order, client, equipment)


class PortalReceiptState(PortalState):
    """Comprovante de uma ordem do próprio cliente, pelo portal."""

    found: bool = False
    back_href: str = "/minha-conta"
    receipt: dict[str, str] = {}
    items: list[dict[str, str]] = []
    payments: list[dict[str, str]] = []
    totals: dict[str, str] = {}

    async def load_portal_receipt(self):
        self.found = False
        redirect = await self._guard_portal()
        if redirect is not None:
            return redirect
        code = str(self.router.page.params.get("codigo", ""))
        self.back_href = "/minha-conta/ordens/" + code
        try:
            service = PortalService(self._gateway(), await self._current())
            item = await service.my_order(code)  # ordens de outros clientes: "não encontrada"
            client = await service.account()
        except NotFoundError:
            self.data_error = ""
            return
        except DataAccessError as error:
            self.data_error = error.user_message
            return
        _show_receipt(self, item.order, client, item.equipment)


class TrackingLinkState(TrackingState):
    """Consulta pública aberta pelo link do QR code: ``/consulta/<código>``."""

    async def load_tracking_link(self):
        await self.load_session()
        raw = str(self.router.page.params.get("codigo", ""))
        code = receipt.normalize_code(raw)
        self.set_tracking_code(code or raw)
        if code is None:  # formato inválido: nenhuma consulta ao backend
            self.tracking_message = NOT_FOUND
            self.tracking_kind = FEEDBACK_ERROR
            return
        await self.lookup_order()
