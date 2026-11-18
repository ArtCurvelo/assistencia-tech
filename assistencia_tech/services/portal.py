"""Portal do cliente: acesso somente às próprias ordens de serviço."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..data.errors import DataAccessError, NotFoundError, ValidationError
from ..data.repositories import DataGateway
from ..domain import order_operations as ops
from ..domain import privacy
from ..domain import rating as rating_rules
from ..domain import service_request
from ..domain.clock import Clock, now_brt
from ..domain.permissions import Permission, Principal, require
from .notifications import get_notifier, notify_order_status
from ..models import Client, Equipment, EquipmentCreate, OrderCreate, ServiceOrder, parse_model


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

    async def _notify(self, order: ServiceOrder) -> None:
        """Avisa o próprio cliente; só lê o cadastro quando o envio de e-mail está ligado."""
        if get_notifier().enabled:
            try:
                client = await self.account()
            except DataAccessError:
                return
            await notify_order_status(self._gw, order, client)

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
        await self._notify(saved)
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

    # ------------------------------------------------------------------
    # Autoatendimento (add-client-self-service)
    # ------------------------------------------------------------------
    async def my_equipment(self) -> list[Equipment]:
        require(self._principal, Permission.PORTAL_EQUIPMENT)
        items = await self._gw.portal.client_equipment(self._client_id())
        return sorted(items, key=lambda e: e.description.casefold())

    async def add_equipment(self, form: Mapping[str, Any]) -> Equipment:
        require(self._principal, Permission.PORTAL_EQUIPMENT)
        client_id = self._client_id()
        # O cliente é sempre o da sessão, nunca um valor vindo do formulário.
        data = parse_model(EquipmentCreate, {**form, "client_id": client_id})
        return await self._gw.portal.add_client_equipment(client_id, data)

    async def request_service(self, form: Mapping[str, Any]) -> PortalOrder:
        """O cliente pede atendimento para um equipamento próprio; a ordem nasce em Solicitado."""
        user = require(self._principal, Permission.PORTAL_REQUEST)
        client_id = self._client_id()
        equipment_id = str(form.get("equipment_id", "")).strip()
        equipment = next((e for e in await self.my_equipment() if e.id == equipment_id), None)
        if equipment is None:
            raise ValidationError("Escolha um dos seus equipamentos.")
        data = parse_model(OrderCreate, {"client_id": client_id, "equipment_id": equipment_id,
                                         "problem": form.get("problem", "")})
        delivery = service_request.parse_delivery(form)
        order = ops.request_service(await self._gw.orders.next_code(), data, delivery, self._clock(),
                                    user.display_name)
        saved = await self._gw.portal.request_service(client_id, order)
        await self._notify(saved)
        return PortalOrder(saved, equipment)
