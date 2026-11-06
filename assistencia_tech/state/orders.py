"""Estado da lista e da abertura de ordens de serviço."""

from __future__ import annotations

import reflex as rx

from ..data.errors import DataAccessError
from ..presenters import matches
from ..services import OrderService
from .base import AdminState

ALL = "todos"


class OrderState(AdminState):
    search: str = ""
    status_filter: str = ALL
    technician_filter: str = ALL

    new_client_id: str = ""
    new_equipment_id: str = ""

    @rx.var
    def filtered_orders(self) -> list[dict[str, str]]:
        return [
            o
            for o in self.orders
            if (self.status_filter == ALL or o["status"] == self.status_filter)
            and (self.technician_filter == ALL or o["technician_id"] == self.technician_filter)
            and matches(o, self.search)
        ]

    @rx.var
    def equipment_options(self) -> list[dict[str, str]]:
        """Somente os equipamentos do cliente escolhido na abertura da OS."""
        return [
            {"value": e["id"], "label": e["label"]} for e in self.equipment if e["client_id"] == self.new_client_id
        ]

    def set_search(self, value: str):
        self.search = value

    def set_status_filter(self, value: str):
        self.status_filter = value

    def set_technician_filter(self, value: str):
        self.technician_filter = value

    def set_new_client(self, value: str):
        self.new_client_id = value
        self.new_equipment_id = ""

    def set_new_equipment(self, value: str):
        self.new_equipment_id = value

    async def open_order(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            form = {
                "client_id": self.new_client_id,
                "equipment_id": self.new_equipment_id,
                "problem": form_data.get("problem", ""),
            }
            created = await OrderService(self._gateway()).open(form)
            await self._reload()
            self.new_client_id = ""
            self.new_equipment_id = ""
            yield self._succeed(f"Ordem {created.code} aberta com sucesso.")
            yield rx.redirect(f"/admin/ordens/{created.code}")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False
