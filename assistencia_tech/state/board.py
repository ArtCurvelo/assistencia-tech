"""Estado do quadro Kanban das ordens (mudança add-orders-board)."""

from __future__ import annotations

from ..data.errors import DataAccessError
from ..domain.permissions import Permission
from ..presenters import board_columns
from ..services import OrderService, load_catalog
from .base import AdminState


class BoardState(AdminState):
    columns: list[dict[str, str]] = []
    cards: dict[str, list[dict[str, str]]] = {}

    async def _load_board(self) -> None:
        principal = await self._current()
        catalog = await load_catalog(self._gateway(), principal)
        self.columns, self.cards = board_columns(catalog, principal)
        self.data_error = ""

    async def load_board(self):
        """``on_load`` próprio: o herdado executaria o carregamento do painel."""
        self._clear_feedback()
        redirect = await self._guard(Permission.ORDERS_VIEW)
        if redirect is not None:
            return redirect
        try:
            await self._load_board()
        except DataAccessError as error:
            self.data_error = error.user_message

    async def move(self, code: str, target: str):
        if not self._start():
            return
        yield
        try:
            await OrderService(self._gateway(), await self._current()).change_status(code, target)
            await self._load_board()
            yield self._succeed(f"{code} movida para {target}.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False
