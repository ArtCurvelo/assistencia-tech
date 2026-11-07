"""Serviço de aplicação do estoque de peças (mudança add-parts-inventory)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.errors import ValidationError
from ..data.repositories import DataGateway
from ..domain.inventory import needs_restock
from ..domain.permissions import Permission as P
from ..domain.permissions import Principal, require
from ..models import Part, PartCreate, StockMovement, parse_model


def parse_quantity(value: Any, label: str = "Quantidade") -> int:
    text = str(value if value is not None else "").strip()
    if not text.isdigit() or int(text) <= 0:
        raise ValidationError(f"{label}: informe um número inteiro maior que zero.")
    return int(text)


def _part_form(form: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(form)
    if "active" in data and isinstance(data["active"], str):
        data["active"] = data["active"].strip().lower() in ("1", "true", "on", "sim", "ativa")
    return data


class InventoryService:
    def __init__(self, gateway: DataGateway, principal: Principal | None) -> None:
        self._gw = gateway
        self._principal = principal

    def _actor(self, permission: P) -> Principal:
        return require(self._principal, permission)

    async def list(self) -> list[Part]:
        self._actor(P.STOCK_VIEW)
        return await self._gw.parts.list()

    async def movements(self) -> list[StockMovement]:
        self._actor(P.STOCK_VIEW)
        return await self._gw.parts.movements()

    async def low_stock(self) -> list[Part]:
        return [p for p in await self.list() if needs_restock(p)]

    async def _ensure_unique_code(self, code: str, exclude_id: str | None = None) -> None:
        for other in await self._gw.parts.list():
            if other.id != exclude_id and other.code == code:
                raise ValidationError(f"Já existe uma peça com o código {code}.")

    async def create(self, form: Mapping[str, Any]) -> Part:
        self._actor(P.STOCK_MANAGE)
        data = parse_model(PartCreate, _part_form(form))
        await self._ensure_unique_code(data.code)
        return await self._gw.parts.create(data)

    async def update(self, part_id: str, form: Mapping[str, Any]) -> Part:
        self._actor(P.STOCK_MANAGE)
        current = await self._gw.parts.get(part_id)
        data = parse_model(PartCreate, {"active": current.active, **_part_form(form)})
        await self._ensure_unique_code(data.code, exclude_id=part_id)
        return await self._gw.parts.update(Part(id=part_id, quantity=current.quantity, **data.model_dump()))

    async def restock(self, part_id: str, quantity: Any, note: str = "") -> Part:
        user = self._actor(P.STOCK_MANAGE)
        amount = parse_quantity(quantity)
        await self._gw.parts.get(part_id)
        return await self._gw.parts.restock(part_id, amount, user.display_name, (note or "").strip())
