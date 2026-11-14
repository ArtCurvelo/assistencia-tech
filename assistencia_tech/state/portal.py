"""Estado do portal do cliente."""

from __future__ import annotations

import json

import reflex as rx

from ..data.errors import DataAccessError, NotFoundError
from ..domain.permissions import Permission
from ..models import OrderStatus
from ..domain import rating as rating_rules
from ..presenters import (
    account_row,
    item_rows,
    payment_rows,
    portal_order_row,
    portal_timeline,
    rating_row,
    totals_row,
)
from ..services import PortalService
from ..domain import privacy
from .base import FEEDBACK_ERROR, AppState


class PortalState(AppState):
    account: dict[str, str] = {}
    my_orders: list[dict[str, str]] = []
    delete_open: bool = False  # diálogo de exclusão da conta (add-lgpd-portal)

    async def _guard_portal(self):
        redirect = await self._guard(Permission.PORTAL_VIEW)
        if redirect is not None and self.is_staff:
            return rx.redirect("/admin")  # colaboradores usam o painel
        return redirect

    async def load_portal(self):
        self._clear_feedback()
        redirect = await self._guard_portal()
        if redirect is not None:
            return redirect
        try:
            service = PortalService(self._gateway(), await self._current())
            self.account = account_row(await service.account())
            self.my_orders = [portal_order_row(p.order, p.equipment) for p in await service.my_orders()]
            self.data_error = ""
        except DataAccessError as error:
            self.data_error = error.user_message


    def set_delete_open(self, value: bool):
        self.delete_open = value
        self._clear_feedback()

    async def download_my_data(self):
        """LGPD, art. 18: o titular baixa os próprios dados em JSON."""
        try:
            data = await PortalService(self._gateway(), await self._current()).export_data()
        except DataAccessError as error:
            return self._fail(error)
        return rx.download(data=json.dumps(data, ensure_ascii=False, indent=2), filename=privacy.EXPORT_FILENAME)

    async def confirm_delete_account(self, form_data: dict):
        if str(form_data.get("confirmation", "")).strip().upper() != "EXCLUIR":
            self.feedback_message = "Digite EXCLUIR para confirmar."
            self.feedback_kind = FEEDBACK_ERROR
            return
        if not self._start():
            return
        yield
        try:
            await PortalService(self._gateway(), await self._current()).delete_account(
                str(form_data.get("password", "")))
        except DataAccessError as error:
            self.is_loading = False
            self.feedback_message = error.user_message
            self.feedback_kind = FEEDBACK_ERROR
            yield
            return
        self.is_loading = False
        self.delete_open = False
        yield rx.toast.success("Sua conta foi excluída e os seus dados pessoais foram anonimizados.")
        yield self.logout()


class PortalOrderState(PortalState):
    found: bool = False
    can_decide: bool = False
    refuse_open: bool = False
    order: dict[str, str] = {}
    items: list[dict[str, str]] = []
    payments: list[dict[str, str]] = []
    timeline: list[dict[str, str]] = []
    totals: dict[str, str] = {}
    rating: dict[str, str] = {}
    can_rate: bool = False
    rate_score: str = ""  # nota escolhida no formulário (add-service-rating)
    rating_question: str = rating_rules.QUESTION

    async def load_portal_order(self):
        self._clear_feedback()
        self.found = False
        redirect = await self._guard_portal()
        if redirect is not None:
            return redirect
        code = str(self.router.page.params.get("codigo", ""))
        try:
            item = await PortalService(self._gateway(), await self._current()).my_order(code)
        except NotFoundError:
            self.data_error = ""
            return
        except DataAccessError as error:
            self.data_error = error.user_message
            return
        self._show(item)

    def _show(self, item) -> None:
        self.can_decide = (
            item.order.status == OrderStatus.AWAITING_APPROVAL
            and Permission.PORTAL_DECIDE_BUDGET.value in self.user_permissions
        )
        self.order = portal_order_row(item.order, item.equipment)
        self.items = item_rows(item.order)
        self.payments = payment_rows(item.order)
        self.timeline = portal_timeline(item.order)
        self.totals = totals_row(item.order)
        self.rating = rating_row(item.order)
        self.can_rate = (
            item.order.status == OrderStatus.DELIVERED
            and item.order.rating is None
            and Permission.PORTAL_RATE.value in self.user_permissions
        )
        self.rate_score = ""
        self.found = True
        self.data_error = ""

    def set_refuse_open(self, value: bool):
        self.refuse_open = value

    async def _decide(self, approve: bool, reason: str, message: str):
        if not self._start():
            return
        yield
        try:
            service = PortalService(self._gateway(), await self._current())
            item = await service.decide_budget(self.order.get("code", ""), approve, reason)
            self._show(item)
            self.refuse_open = False
            yield self._succeed(message)
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    async def approve_budget(self):
        async for event in self._decide(True, "", "Orçamento aprovado. O reparo será iniciado."):
            yield event

    async def confirm_refusal(self, form_data: dict):
        reason = str(form_data.get("reason", ""))
        async for event in self._decide(False, reason, "Orçamento recusado. A ordem foi cancelada."):
            yield event

    def choose_score(self, score: str):
        self.rate_score = score

    async def submit_rating(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            service = PortalService(self._gateway(), await self._current())
            item = await service.rate(self.order.get("code", ""), self.rate_score, form_data.get("comment", ""))
            self._show(item)
            yield self._succeed("Obrigado pela sua avaliação!")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False
