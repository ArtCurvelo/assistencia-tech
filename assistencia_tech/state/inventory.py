"""Estado da página de estoque: catálogo, cadastro, edição, entrada e movimentações."""

from __future__ import annotations

import reflex as rx

from ..data.errors import DataAccessError
from ..domain.permissions import Permission
from ..presenters import matches, movement_row, part_row
from ..services import InventoryService
from .base import AdminState

MOVEMENTS_SHOWN = 30


class InventoryState(AdminState):
    parts: list[dict[str, str]] = []
    movements: list[dict[str, str]] = []
    search: str = ""
    form_key: int = 0

    edit_open: bool = False
    edit_id: str = ""
    edit_values: dict[str, str] = {}

    restock_open: bool = False
    restock_id: str = ""
    restock_name: str = ""

    def _required_permission(self) -> Permission:
        return Permission.STOCK_VIEW

    async def load_inventory(self):
        """``on_load`` da página de estoque."""
        self._clear_feedback()
        redirect = await self._guard(Permission.STOCK_VIEW)
        if redirect is not None:
            return redirect
        try:
            await self._reload()
        except DataAccessError as error:
            self.data_error = error.user_message

    async def _reload(self) -> None:
        service = InventoryService(self._gateway(), await self._current())
        parts = await service.list()
        by_id = {p.id: p for p in parts}
        self.parts = [part_row(p) for p in parts]
        self.movements = [movement_row(m, by_id) for m in (await service.movements())[:MOVEMENTS_SHOWN]]
        self.low_stock_count = sum(1 for p in self.parts if p["level"] in ("Baixo", "Esgotado"))
        self.data_error = ""

    @rx.var
    def filtered_parts(self) -> list[dict[str, str]]:
        return [p for p in self.parts if matches(p, self.search)]

    def set_search(self, value: str):
        self.search = value

    async def _act(self, action, message):
        if not self._start():
            return
        yield
        try:
            result = await action(InventoryService(self._gateway(), await self._current()))
            await self._reload()
            self.edit_open = False
            self.restock_open = False
            yield self._succeed(message(result))
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    async def add_part(self, form_data: dict):
        async for event in self._act(lambda s: s.create(form_data), lambda p: f"Peça {p.name} cadastrada."):
            yield event
        if self.feedback_kind == "success":
            self.form_key += 1  # limpa o formulário só depois de cadastrar

    def open_edit(self, part: dict):
        self._clear_feedback()
        self.edit_id = part["id"]
        self.edit_values = {
            "code": part["code"],
            "name": part["name"],
            "unit_price": part["price_input"],
            "min_quantity": part["min_quantity"],
            "active": part["active"],
        }
        self.edit_open = True

    def set_edit_open(self, value: bool):
        self.edit_open = value

    async def save_edit(self, form_data: dict):
        form = {**form_data, "active": form_data.get("active", self.edit_values.get("active", "sim")) == "sim"}
        async for event in self._act(lambda s: s.update(self.edit_id, form), lambda p: f"Peça {p.name} atualizada."):
            yield event

    def open_restock(self, part: dict):
        self._clear_feedback()
        self.restock_id = part["id"]
        self.restock_name = part["name"]
        self.restock_open = True

    def set_restock_open(self, value: bool):
        self.restock_open = value

    async def confirm_restock(self, form_data: dict):
        quantity, note = form_data.get("quantity", ""), str(form_data.get("note", ""))
        async for event in self._act(
            lambda s: s.restock(self.restock_id, quantity, note),
            lambda p: f"Entrada registrada: {p.name} agora tem {p.quantity} unidade(s).",
        ):
            yield event
