"""Estado das páginas de clientes (lista, edição, exclusão e detalhe)."""

from __future__ import annotations

import reflex as rx

from ..data.errors import DataAccessError, NotFoundError
from ..presenters import client_row, equipment_row, matches, order_row
from ..services import ClientService, load_catalog
from ..domain.permissions import Permission
from .base import AdminState


class ClientState(AdminState):
    search: str = ""
    form_key: int = 0  # muda só após sucesso: o formulário recusado mantém os dados

    def _required_permission(self) -> Permission:
        return Permission.CLIENTS_VIEW

    edit_open: bool = False
    edit_id: str = ""
    edit_values: dict[str, str] = {}

    delete_open: bool = False
    delete_id: str = ""
    delete_name: str = ""

    @rx.var
    def filtered_clients(self) -> list[dict[str, str]]:
        return [c for c in self.clients if matches(c, self.search)]

    def set_search(self, value: str):
        self.search = value

    # ------------------------------------------------------------ cadastro
    async def add_client(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            created = await ClientService(self._gateway(), await self._current()).create(form_data)
            await self._reload()
            self.form_key += 1
            yield self._succeed(f"Cliente {created.name} cadastrado com sucesso.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    # -------------------------------------------------------------- edição
    def open_edit(self, client: dict):
        self._clear_feedback()
        self.edit_id = client["id"]
        self.edit_values = {k: client[k] for k in ("name", "cpf", "email", "phone")}
        self.edit_open = True

    def set_edit_open(self, value: bool):
        self.edit_open = value

    async def save_edit(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            updated = await ClientService(self._gateway(), await self._current()).update(self.edit_id, form_data)
            await self._reload()
            self.edit_open = False
            yield self._succeed(f"Dados de {updated.name} atualizados.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    # ------------------------------------------------------------ exclusão
    def ask_delete(self, client: dict):
        self._clear_feedback()
        self.delete_id = client["id"]
        self.delete_name = client["name"]
        self.delete_open = True

    def set_delete_open(self, value: bool):
        self.delete_open = value

    async def confirm_delete(self):
        if not self._start():
            return
        yield
        try:
            removed = await ClientService(self._gateway(), await self._current()).delete(self.delete_id)
            await self._reload()
            yield self._succeed(f"Cliente {removed.name} excluído.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.delete_open = False
            self.is_loading = False


class ClientDetailState(AdminState):
    found: bool = False
    client: dict[str, str] = {}
    client_equipment: list[dict[str, str]] = []
    client_orders: list[dict[str, str]] = []

    async def load_client(self):
        self._clear_feedback()
        self.found = False
        redirect = await self._guard(Permission.CLIENTS_VIEW)
        if redirect is not None:
            return redirect
        client_id = str(self.router.page.params.get("cliente_id", ""))
        try:
            gateway = self._gateway()
            detail = await ClientService(gateway, await self._current()).detail(client_id)
            catalog = await load_catalog(gateway, await self._current())
        except NotFoundError:
            self.data_error = ""
            return
        except DataAccessError as error:
            self.data_error = error.user_message
            return
        self.client = client_row(detail.client)
        self.client_equipment = [equipment_row(e, catalog) for e in detail.equipment]
        self.client_orders = [order_row(o, catalog) for o in detail.orders]
        self.found = True
        self.data_error = ""
