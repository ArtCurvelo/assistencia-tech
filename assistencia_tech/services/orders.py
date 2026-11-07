"""Serviço de aplicação de ordens de serviço."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

from ..data.errors import NotFoundError, ValidationError
from ..data.repositories import DataGateway
from ..domain import deadlines
from ..domain import order_operations as ops
from ..domain.inventory import ensure_available
from .inventory import parse_quantity
from ..domain.clock import Clock, now_brt
from ..domain.permissions import Permission as P
from ..domain.permissions import Principal, ensure_can_modify_order, require, status_permission
from ..domain.order_workflow import parse_status
from ..models import (
    ItemKind,
    OrderCreate,
    OrderItemCreate,
    PaymentCreate,
    PublicOrderView,
    ServiceOrder,
    Technician,
    parse_model,
)

Mutation = Callable[[ServiceOrder, datetime], ServiceOrder]


class OrderService:
    def __init__(self, gateway: DataGateway, principal: Principal | None, *, clock: Clock = now_brt) -> None:
        self._gw = gateway
        self._principal = principal
        self._clock = clock

    @property
    def _actor(self) -> str:
        # Autor do histórico: nome e perfil do usuário autenticado.
        return self._principal.display_name if self._principal else "Sistema"

    async def list(self) -> list[ServiceOrder]:
        require(self._principal, P.ORDERS_VIEW)
        return await self._gw.orders.list()

    async def get(self, code: str) -> ServiceOrder:
        require(self._principal, P.ORDERS_VIEW)
        return await self._gw.orders.get_by_code(code)

    async def open(self, form: Mapping[str, Any]) -> ServiceOrder:
        require(self._principal, P.ORDERS_OPEN)
        # O vínculo de garantia só nasce por ``open_warranty``, a partir da ordem original.
        data = parse_model(OrderCreate, {k: v for k, v in form.items() if k != "warranty_of"})
        return await self._open(data)

    async def open_warranty(self, original_code: str, form: Mapping[str, Any]) -> ServiceOrder:
        """Ordem em garantia: mesmo cliente e equipamento da original, dentro de 90 dias da entrega."""
        require(self._principal, P.ORDERS_OPEN)
        original = await self._gw.orders.get_by_code(original_code)
        data = parse_model(OrderCreate, {
            "client_id": original.client_id,
            "equipment_id": original.equipment_id,
            "problem": form.get("problem", ""),
            "due_date": form.get("due_date") or None,
            "warranty_of": original.code,
        })
        deadlines.ensure_warranty_eligible(original, data.client_id, data.equipment_id, self._clock().date())
        return await self._open(data)

    async def set_due_date(self, code: str, value: Any) -> ServiceOrder:
        require(self._principal, P.ORDERS_ASSIGN)
        due = parse_model(OrderCreate, {"client_id": "-", "equipment_id": "-", "problem": "-",
                                        "due_date": value}).due_date
        return await self._mutate(code, P.ORDERS_ASSIGN, lambda o, at: ops.set_due_date(o, due, at, self._actor))

    async def _open(self, data: OrderCreate) -> ServiceOrder:
        client = await self._gw.clients.get(data.client_id)
        equipment = await self._gw.equipment.get(data.equipment_id)
        if equipment.client_id != client.id:
            raise ValidationError(f"O equipamento selecionado não pertence ao cliente {client.name}.")
        code = await self._gw.orders.next_code()
        order = ops.open_order(code, data, self._clock(), self._actor)
        return await self._gw.orders.create(order)

    async def _mutate(self, code: str, permission: P, change: Mutation) -> ServiceOrder:
        user = require(self._principal, permission)
        order = await self._gw.orders.get_by_code(code)
        ensure_can_modify_order(user, order)
        return await self._gw.orders.save(change(order, self._clock()))

    async def _technician(self, technician_id: str | None) -> Technician | None:
        if not technician_id:
            return None
        for technician in await self._gw.technicians.list():
            if technician.id == technician_id:
                return technician
        raise NotFoundError("Técnico não encontrado.")

    async def assign_technician(self, code: str, technician_id: str) -> ServiceOrder:
        require(self._principal, P.ORDERS_ASSIGN)
        if not technician_id:
            raise ValidationError("Selecione um técnico.")
        technician = await self._technician(technician_id)
        if technician is not None and not technician.active:
            raise ValidationError(f"{technician.name} está inativo e não pode receber novas ordens.")
        order = await self._gw.orders.get_by_code(code)
        previous = await self._technician(order.technician_id)
        updated = ops.assign_technician(order, technician, previous, self._clock(), self._actor)
        return await self._gw.orders.save(updated)

    async def record_diagnosis(self, code: str, text: str) -> ServiceOrder:
        return await self._mutate(code, P.ORDERS_DIAGNOSE, lambda o, at: ops.record_diagnosis(o, text, at, self._actor))

    async def _catalog_item(self, form: Mapping[str, Any]) -> OrderItemCreate:
        """Peça do catálogo: nome e preço do estoque, com quantidade disponível (D1 de add-parts-inventory)."""
        part = await self._gw.parts.get(str(form["part_id"]))
        quantity = parse_quantity(form.get("quantity") or 1)
        ensure_available(part, quantity)
        return OrderItemCreate(kind=ItemKind.PART, description=part.name, quantity=quantity,
                               unit_price=part.unit_price, part_id=part.id)

    async def add_item(self, code: str, form: Mapping[str, Any]) -> ServiceOrder:
        require(self._principal, P.ORDERS_DIAGNOSE)
        if str(form.get("part_id") or "").strip():
            data = await self._catalog_item(form)
        else:
            data = parse_model(OrderItemCreate, {k: v for k, v in form.items() if k != "part_id"})
        return await self._mutate(code, P.ORDERS_DIAGNOSE, lambda o, at: ops.add_item(o, data, at, self._actor))

    async def remove_item(self, code: str, item_id: str) -> ServiceOrder:
        return await self._mutate(code, P.ORDERS_DIAGNOSE, lambda o, at: ops.remove_item(o, item_id, at, self._actor))

    async def add_payment(self, code: str, form: Mapping[str, Any]) -> ServiceOrder:
        require(self._principal, P.ORDERS_PAYMENTS)
        data = parse_model(PaymentCreate, form)
        return await self._mutate(code, P.ORDERS_PAYMENTS, lambda o, at: ops.add_payment(o, data, at, self._actor))

    async def change_status(self, code: str, target: str, reason: str = "") -> ServiceOrder:
        user = require(self._principal, P.ORDERS_VIEW)
        order = await self._gw.orders.get_by_code(code)
        require(user, status_permission(order.status, parse_status(target)))
        ensure_can_modify_order(user, order)
        updated = ops.change_status(order, target, self._clock(), self._actor, reason)
        return await self._gw.orders.save(updated)

    async def public_view(self, code: str) -> PublicOrderView:
        if not code.strip():
            raise ValidationError("Informe o código da ordem de serviço.")
        return await self._gw.portal.public_order(code.strip())
