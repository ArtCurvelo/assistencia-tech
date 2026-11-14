"""Portal do cliente: acesso somente às próprias ordens de serviço."""

from __future__ import annotations

from dataclasses import dataclass

from ..data.errors import NotFoundError, ValidationError
from ..data.repositories import DataGateway
from ..domain import order_operations as ops
from ..domain import privacy
from ..domain import rating as rating_rules
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

    async def rate(self, code: str, score: object, comment: object = "") -> PortalOrder:
        """O cliente avalia uma ordem própria entregue, uma única vez (add-service-rating)."""
        require(self._principal, Permission.PORTAL_RATE)
        client_id = self._client_id()
        item = await self.my_order(code)
        rated = rating_rules.rate(item.order, score, comment, self._clock())
        saved = await self._gw.portal.save_rating(client_id, rated)
        return PortalOrder(saved, item.equipment)

    async def export_data(self) -> dict:
        """Dados do próprio titular para download (LGPD, art. 18; add-lgpd-portal)."""
        client = await self.account()
        items = await self.my_orders()
        return privacy.export_data(client, [(i.order, i.equipment) for i in items], self._clock())

    async def delete_account(self, password: str) -> None:
        """Anonimiza o cadastro e desativa o login do titular, mantendo as ordens."""
        user = require(self._principal, Permission.PORTAL_VIEW)
        client_id = self._client_id()
        if not (password or "").strip():
            raise ValidationError("Informe a sua senha para confirmar.")
        privacy.ensure_can_delete(item.order for item in await self.my_orders())
        await self._gw.portal.delete_account(user.user_id, client_id, password)
