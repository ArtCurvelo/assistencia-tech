"""Portal do cliente: acesso somente às próprias ordens de serviço."""

from __future__ import annotations

from dataclasses import dataclass

from ..data.errors import NotFoundError
from ..data.repositories import DataGateway
from ..domain import order_operations as ops
from ..domain.clock import Clock, now_brt
from ..domain.permissions import Permission, Principal, require
from ..models import Client, Equipment, ServiceOrder


@dataclass(frozen=True)
class PortalOrder:
    order: ServiceOrder
    equipment: Equipment | None


class PortalService:
    def __init__(self, gateway: DataGateway, principal: Principal | None, *, clock: Clock = now_brt) -> None:
        self._gw = gateway
        self._principal = principal
        self._clock = clock

    def _client_id(self) -> str:
        user = require(self._principal, Permission.PORTAL_VIEW)
        if not user.client_id:
            raise NotFoundError("Conta sem cliente associado.")
        return user.client_id

    async def account(self) -> Client:
        return await self._gw.portal.client_account(self._client_id())

    async def my_orders(self) -> list[PortalOrder]:
        pairs = await self._gw.portal.client_orders(self._client_id())
        pairs.sort(key=lambda pair: pair[0].updated_at, reverse=True)
        return [PortalOrder(order, equipment) for order, equipment in pairs]

    async def my_order(self, code: str) -> PortalOrder:
        wanted = code.strip().upper()
        # Somente as ordens do próprio cliente: as demais recebem "não encontrada".
        for item in await self.my_orders():
            if item.order.code.upper() == wanted:
                return item
        raise NotFoundError("Ordem de serviço não encontrada.")

    async def decide_budget(self, code: str, approve: bool, reason: str = "") -> PortalOrder:
        """O cliente aprova ou recusa o orçamento de uma ordem própria em "Aguardando aprovação"."""
        user = require(self._principal, Permission.PORTAL_DECIDE_BUDGET)
        client_id = self._client_id()
        item = await self.my_order(code)
        updated = ops.client_decision(item.order, approve, reason, self._clock(), user.display_name)
        saved = await self._gw.portal.save_client_decision(client_id, updated, approve, (reason or "").strip())
        return PortalOrder(saved, item.equipment)
