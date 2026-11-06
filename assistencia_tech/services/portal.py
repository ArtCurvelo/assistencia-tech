"""Portal do cliente: acesso somente às próprias ordens de serviço."""

from __future__ import annotations

from dataclasses import dataclass

from ..data.errors import NotFoundError
from ..data.repositories import DataGateway
from ..domain.permissions import Permission, Principal, require
from ..models import Client, Equipment, ServiceOrder


@dataclass(frozen=True)
class PortalOrder:
    order: ServiceOrder
    equipment: Equipment | None


class PortalService:
    def __init__(self, gateway: DataGateway, principal: Principal | None) -> None:
        self._gw = gateway
        self._principal = principal

    def _client_id(self) -> str:
        user = require(self._principal, Permission.PORTAL_VIEW)
        if not user.client_id:
            raise NotFoundError("Conta sem cliente associado.")
        return user.client_id

    async def account(self) -> Client:
        return await self._gw.clients.get(self._client_id())

    async def _equipment(self, equipment_id: str) -> Equipment | None:
        try:
            return await self._gw.equipment.get(equipment_id)
        except NotFoundError:
            return None

    async def my_orders(self) -> list[PortalOrder]:
        client_id = self._client_id()
        orders = [o for o in await self._gw.orders.list() if o.client_id == client_id]
        orders.sort(key=lambda o: o.updated_at, reverse=True)
        return [PortalOrder(o, await self._equipment(o.equipment_id)) for o in orders]

    async def my_order(self, code: str) -> PortalOrder:
        client_id = self._client_id()
        try:
            order = await self._gw.orders.get_by_code(code)
        except NotFoundError:
            order = None
        # Ordens de outros clientes recebem a mesma resposta de "não encontrada".
        if order is None or order.client_id != client_id:
            raise NotFoundError("Ordem de serviço não encontrada.")
        return PortalOrder(order, await self._equipment(order.equipment_id))
