"""Estado da página de equipamentos (cadastro, filtros, edição, exclusão e histórico)."""

from __future__ import annotations

import reflex as rx

from ..data.errors import DataAccessError
from ..presenters import matches, order_row
from ..services import EquipmentService, load_catalog
from .base import AdminState

ALL_KINDS = "Todos"


class EquipmentState(AdminState):
    search: str = ""
    kind_filter: str = ALL_KINDS

    edit_open: bool = False
    edit_id: str = ""
    edit_values: dict[str, str] = {}

    delete_open: bool = False
    delete_id: str = ""
    delete_name: str = ""

    history_open: bool = False
    history_title: str = ""
    history_orders: list[dict[str, str]] = []

    @rx.var
    def filtered_equipment(self) -> list[dict[str, str]]:
        return [
            e
            for e in self.equipment
            if (self.kind_filter == ALL_KINDS or e["kind"] == self.kind_filter) and matches(e, self.search)
        ]

    def set_search(self, value: str):
        self.search = value

    def set_kind_filter(self, value: str):
        self.kind_filter = value

    async def add_equipment(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            created = await EquipmentService(self._gateway()).create(form_data)
            await self._reload()
            yield self._succeed(f"Equipamento {created.description} cadastrado.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    def open_edit(self, equipment: dict):
        self._clear_feedback()
        self.edit_id = equipment["id"]
        self.edit_values = {
            "client_id": equipment["client_id"],
            "kind": equipment["kind"],
            "brand": equipment["brand"],
            "model": equipment["model"],
            "serial_number": equipment["serial"],
            "notes": equipment["notes"],
        }
        self.edit_open = True

    def set_edit_open(self, value: bool):
        self.edit_open = value

    async def save_edit(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            updated = await EquipmentService(self._gateway()).update(self.edit_id, form_data)
            await self._reload()
            self.edit_open = False
            yield self._succeed(f"Equipamento {updated.description} atualizado.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    def ask_delete(self, equipment: dict):
        self._clear_feedback()
        self.delete_id = equipment["id"]
        self.delete_name = equipment["description"]
        self.delete_open = True

    def set_delete_open(self, value: bool):
        self.delete_open = value

    async def confirm_delete(self):
        if not self._start():
            return
        yield
        try:
            removed = await EquipmentService(self._gateway()).delete(self.delete_id)
            await self._reload()
            yield self._succeed(f"Equipamento {removed.description} excluído.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.delete_open = False
            self.is_loading = False

    async def open_history(self, equipment: dict):
        self._clear_feedback()
        try:
            gateway = self._gateway()
            item, orders = await EquipmentService(gateway).history(equipment["id"])
            catalog = await load_catalog(gateway)
        except DataAccessError as error:
            yield self._fail(error)
            return
        self.history_title = item.description
        self.history_orders = [order_row(o, catalog) for o in orders]
        self.history_open = True

    def set_history_open(self, value: bool):
        self.history_open = value
