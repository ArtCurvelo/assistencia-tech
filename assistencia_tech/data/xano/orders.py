"""Ordens de serviço no Xano: o agregado sobre várias tabelas (decisão D13).

``save`` compara a versão gravada com a nova e envia somente as diferenças:
itens novos e removidos, pagamentos novos, campos da ordem e eventos novos do
histórico. O backend repete as regras de status e perfil (veja
``xano/api/atech_os``), então uma mudança recusada lá chega como erro com a
mensagem da pré-condição.
"""

from __future__ import annotations

from typing import Any

from ...models import PublicOrderView, PublicStats, ServiceOrder
from ..errors import NotFoundError, ValidationError
from . import mappers
from .base import XanoRepository

# O id da ordem é atribuído pelo Xano na criação; o código definitivo vem da
# resposta de ``create``. Este valor provisório nunca é gravado.
PROVISIONAL_CODE = "OS-NOVA"


def _ensure_code(order: ServiceOrder, code: str) -> ServiceOrder:
    # O id pertence a uma ordem de outro ano: para o usuário, o código não existe.
    if order.code != mappers.normalize_order_code(code):
        raise NotFoundError(f"Ordem de serviço não encontrada: {code.strip()}.")
    return order


class XanoOrderRepository(XanoRepository):
    async def list(self) -> list[ServiceOrder]:
        orders = [mappers.order_from(r) for r in await self._list("orders.list")]
        return sorted(orders, key=lambda o: (o.opened_at, o.code), reverse=True)

    async def _get(self, order_id: int | str) -> ServiceOrder:
        record = await self._record("orders.get", path_params={"os_servicos_id": order_id})
        return mappers.order_from(record)

    async def get_by_code(self, code: str) -> ServiceOrder:
        _, order_id = mappers.parse_order_code(code)
        return _ensure_code(await self._get(order_id), code)

    async def next_code(self) -> str:
        return PROVISIONAL_CODE

    async def create(self, order: ServiceOrder) -> ServiceOrder:
        record = await self._record(
            "orders.create",
            json={
                "cliente_id": int(order.client_id),
                "item_cliente_id": int(order.equipment_id),
                "descricao_problema": order.problem,
                "status": mappers.STATUS_TO_XANO[order.status],
                **({"previsao_entrega": order.due_date.isoformat()} if order.due_date else {}),
                **({"garantia_de": mappers.parse_order_code(order.warranty_of)[1]} if order.warranty_of else {}),
            },
        )
        order_id = str(record.get("id"))
        for event in order.history:
            await self._call("orders.history.add", json=mappers.event_payload(order_id, event))
        return await self._get(order_id)

    def _order_changes(self, current: ServiceOrder, new: ServiceOrder) -> dict[str, Any]:
        changes: dict[str, Any] = {}
        if new.technician_id != current.technician_id and new.technician_id:
            changes["user_id"] = int(new.technician_id)
        if new.diagnosis != current.diagnosis:
            changes["diagnostico"] = new.diagnosis
        if new.due_date and new.due_date != current.due_date:
            changes["previsao_entrega"] = new.due_date.isoformat()
        if new.status != current.status:
            changes["status"] = mappers.STATUS_TO_XANO[new.status]
            if new.cancel_reason:
                changes["motivo_cancelamento"] = new.cancel_reason
        return changes

    async def save(self, order: ServiceOrder) -> ServiceOrder:
        current = await self.get_by_code(order.code)
        order_id = mappers.order_id_of(current)

        current_items = {i.id for i in current.items}
        new_items = {i.id for i in order.items}
        for item in order.items:
            if item.id not in current_items:
                await self._call("orders.items.add", json=mappers.item_payload(order_id, item))
        for item_id in current_items - new_items:
            await self._call("orders.items.remove", path_params={"os_itens_id": item_id})

        current_payments = {p.id for p in current.payments}
        for payment in order.payments:
            if payment.id not in current_payments:
                await self._call("orders.payments.add", json=mappers.payment_payload(order_id, payment))

        changes = self._order_changes(current, order)
        if changes:
            await self._call("orders.update", path_params={"os_servicos_id": order_id}, json=changes)

        for event in order.history[len(current.history):]:
            await self._call("orders.history.add", json=mappers.event_payload(order_id, event))
        return await self._get(order_id)


class XanoPortalRepository(XanoRepository):
    """Projeções no servidor: consulta pública e portal do cliente (decisão D14)."""

    async def client_account(self, client_id: str):
        client = mappers.client_from(await self._record("portal.client_account"))
        if client.id != client_id:
            raise NotFoundError("Cliente não encontrado.")
        return client

    async def client_orders(self, client_id: str):
        pairs = []
        for record in await self._list("portal.client_orders"):
            order = mappers.order_from(record)
            if order.client_id != client_id:
                continue
            device = record.get("_aparelho")
            pairs.append((order, mappers.equipment_from(device) if isinstance(device, dict) else None))
        return pairs

    async def save_client_decision(
        self, client_id: str, order: ServiceOrder, approve: bool, reason: str
    ) -> ServiceOrder:
        # O backend repete as validações e grava decisão, status e histórico numa transação.
        order_id = int(mappers.order_id_of(order))
        payload = {"os_servicos_id": order_id, "aprovar": approve, "motivo": reason}
        await self._call("portal.client_decision", json=payload)
        for refreshed, _ in await self.client_orders(client_id):
            if refreshed.code == order.code:
                return refreshed
        raise NotFoundError("Ordem de serviço não encontrada.")

    async def save_rating(self, client_id: str, order: ServiceOrder) -> ServiceOrder:
        # O backend repete as validações (dono, entregue, nota, avaliação única).
        rating = order.rating
        if rating is None:
            raise ValidationError("Informe a nota da avaliação.")
        payload = {"os_servicos_id": int(mappers.order_id_of(order)), "nota": rating.score,
                   "comentario": rating.comment}
        await self._call("portal.client_rating", json=payload)
        for refreshed, _ in await self.client_orders(client_id):
            if refreshed.code == order.code:
                return refreshed
        raise NotFoundError("Ordem de serviço não encontrada.")

    async def public_stats(self) -> PublicStats:
        return mappers.public_stats_from(await self._record("portal.public_stats"))

    async def public_order(self, code: str) -> PublicOrderView:
        _, order_id = mappers.parse_order_code(code)
        record = await self._record("portal.public_order", path_params={"os_servicos_id": order_id})
        view = mappers.public_view_from(record)
        if view.code != mappers.normalize_order_code(code):
            raise NotFoundError(f"Ordem de serviço não encontrada: {code.strip()}.")
        return view
