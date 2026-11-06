"""Serviço de aplicação de ordens de serviço."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

from ..data.errors import NotFoundError, ValidationError
from ..data.repositories import DataGateway
from ..domain import order_operations as ops
from ..domain.clock import DEFAULT_ACTOR, Clock, now_brt
from ..models import (
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
    def __init__(self, gateway: DataGateway, *, clock: Clock = now_brt, actor: str = DEFAULT_ACTOR) -> None:
        self._gw = gateway
        self._clock = clock
        self._actor = actor

    async def list(self) -> list[ServiceOrder]:
        return await self._gw.orders.list()

    async def get(self, code: str) -> ServiceOrder:
        return await self._gw.orders.get_by_code(code)

    async def open(self, form: Mapping[str, Any]) -> ServiceOrder:
        data = parse_model(OrderCreate, form)
        client = await self._gw.clients.get(data.client_id)
        equipment = await self._gw.equipment.get(data.equipment_id)
        if equipment.client_id != client.id:
            raise ValidationError(f"O equipamento selecionado não pertence ao cliente {client.name}.")
        code = await self._gw.orders.next_code()
        order = ops.open_order(code, data, self._clock(), self._actor)
        return await self._gw.orders.create(order)

    async def _mutate(self, code: str, change: Mutation) -> ServiceOrder:
        order = await self._gw.orders.get_by_code(code)
        return await self._gw.orders.save(change(order, self._clock()))

    async def _technician(self, technician_id: str | None) -> Technician | None:
        if not technician_id:
            return None
        for technician in await self._gw.technicians.list():
            if technician.id == technician_id:
                return technician
        raise NotFoundError("Técnico não encontrado.")

    async def assign_technician(self, code: str, technician_id: str) -> ServiceOrder:
        if not technician_id:
            raise ValidationError("Selecione um técnico.")
        technician = await self._technician(technician_id)
        order = await self._gw.orders.get_by_code(code)
        previous = await self._technician(order.technician_id)
        updated = ops.assign_technician(order, technician, previous, self._clock(), self._actor)
        return await self._gw.orders.save(updated)

    async def record_diagnosis(self, code: str, text: str) -> ServiceOrder:
        return await self._mutate(code, lambda o, at: ops.record_diagnosis(o, text, at, self._actor))

    async def add_item(self, code: str, form: Mapping[str, Any]) -> ServiceOrder:
        data = parse_model(OrderItemCreate, form)
        return await self._mutate(code, lambda o, at: ops.add_item(o, data, at, self._actor))

    async def remove_item(self, code: str, item_id: str) -> ServiceOrder:
        return await self._mutate(code, lambda o, at: ops.remove_item(o, item_id, at, self._actor))

    async def add_payment(self, code: str, form: Mapping[str, Any]) -> ServiceOrder:
        data = parse_model(PaymentCreate, form)
        return await self._mutate(code, lambda o, at: ops.add_payment(o, data, at, self._actor))

    async def change_status(self, code: str, target: str, reason: str = "") -> ServiceOrder:
        return await self._mutate(code, lambda o, at: ops.change_status(o, target, at, self._actor, reason))

    async def public_view(self, code: str) -> PublicOrderView:
        if not code.strip():
            raise ValidationError("Informe o código da ordem de serviço.")
        order = await self._gw.orders.get_by_code(code)
        try:
            equipment = (await self._gw.equipment.get(order.equipment_id)).description
        except NotFoundError:
            equipment = "Equipamento"
        return PublicOrderView(code=order.code, status=order.status, equipment=equipment, updated_at=order.updated_at)
