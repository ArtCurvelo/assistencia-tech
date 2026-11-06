"""Serviço de aplicação de equipamentos."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.errors import ValidationError
from ..data.repositories import DataGateway
from ..models import Equipment, EquipmentCreate, ServiceOrder, parse_model, serial_key


class EquipmentService:
    def __init__(self, gateway: DataGateway) -> None:
        self._gw = gateway

    async def list(self) -> list[Equipment]:
        return await self._gw.equipment.list()

    async def _orders_of(self, equipment_id: str) -> list[ServiceOrder]:
        orders = [o for o in await self._gw.orders.list() if o.equipment_id == equipment_id]
        return sorted(orders, key=lambda o: o.opened_at, reverse=True)

    async def _ensure_serial_unique(self, data: EquipmentCreate, exclude_id: str | None = None) -> None:
        key = serial_key(data.serial_number)
        if not key:
            return
        for other in await self._gw.equipment.list():
            if other.id != exclude_id and serial_key(other.serial_number) == key:
                raise ValidationError(f"O número de série {data.serial_number} já está cadastrado.")

    async def create(self, form: Mapping[str, Any]) -> Equipment:
        data = parse_model(EquipmentCreate, form)
        await self._gw.clients.get(data.client_id)
        await self._ensure_serial_unique(data)
        return await self._gw.equipment.create(data)

    async def update(self, equipment_id: str, form: Mapping[str, Any]) -> Equipment:
        current = await self._gw.equipment.get(equipment_id)
        data = parse_model(EquipmentCreate, form)
        if data.client_id != current.client_id:
            if await self._orders_of(equipment_id):
                raise ValidationError(
                    "O cliente deste equipamento não pode ser alterado porque já existem ordens de serviço."
                )
            await self._gw.clients.get(data.client_id)
        await self._ensure_serial_unique(data, exclude_id=equipment_id)
        return await self._gw.equipment.update(Equipment(id=equipment_id, **data.model_dump()))

    async def delete(self, equipment_id: str) -> Equipment:
        equipment = await self._gw.equipment.get(equipment_id)
        orders = await self._orders_of(equipment_id)
        if orders:
            count = len(orders)
            label = "ordem de serviço vinculada" if count == 1 else "ordens de serviço vinculadas"
            raise ValidationError(f"Não é possível excluir {equipment.description}: há {count} {label}.")
        await self._gw.equipment.delete(equipment_id)
        return equipment

    async def history(self, equipment_id: str) -> tuple[Equipment, list[ServiceOrder]]:
        equipment = await self._gw.equipment.get(equipment_id)
        return equipment, await self._orders_of(equipment_id)
