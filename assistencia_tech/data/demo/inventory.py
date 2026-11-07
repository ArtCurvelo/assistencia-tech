"""Estoque de peças do modo demonstração (memória)."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from ...domain.clock import Clock, now_brt
from ...domain.inventory import StockEffect
from ...models import MovementKind, Part, PartCreate, StockMovement
from ..errors import NotFoundError, ValidationError


def seed_parts() -> list[Part]:
    rows = [
        ("1", "SSD-480", "SSD 480 GB", "250.00", 6, 2),
        ("2", "FNT-65W", "Fonte 65 W para notebook", "180.00", 3, 2),
        ("3", "PST-TER", "Pasta térmica (seringa)", "35.00", 12, 4),
        ("4", "BAT-6C", "Bateria 6 células", "290.00", 1, 2),
        ("5", "TEC-ABNT", "Teclado ABNT2 para notebook", "160.00", 0, 1),
        ("6", "MEM-8GB", "Memória DDR4 8 GB", "220.00", 4, 1),
    ]
    return [
        Part(id=i, code=c, name=n, unit_price=Decimal(p), quantity=q, min_quantity=m)
        for i, c, n, p, q, m in rows
    ]


class DemoPartRepository:
    def __init__(self, items: list[Part], *, clock: Clock = now_brt) -> None:
        self.items = list(items)
        self.history: list[StockMovement] = []
        self._clock = clock

    async def list(self) -> list[Part]:
        return sorted(self.items, key=lambda p: p.name.casefold())

    def _find(self, part_id: str) -> Part:
        for part in self.items:
            if part.id == part_id:
                return part
        raise NotFoundError("Peça não encontrada.")

    async def get(self, part_id: str) -> Part:
        return self._find(part_id)

    def _replace(self, part: Part) -> Part:
        self.items = [part if p.id == part.id else p for p in self.items]
        return part

    async def create(self, data: PartCreate) -> Part:
        if any(p.code == data.code for p in self.items):
            raise ValidationError(f"Já existe uma peça com o código {data.code}.")
        next_id = str(max((int(p.id) for p in self.items if p.id.isdigit()), default=0) + 1)
        part = Part(id=next_id, quantity=0, **data.model_dump())
        self.items.append(part)
        return part

    async def update(self, part: Part) -> Part:
        current = self._find(part.id)
        return self._replace(part.model_copy(update={"quantity": current.quantity}))

    def _move(self, part_id: str, kind: MovementKind, quantity: int, author: str, order_code: str, note: str) -> Part:
        part = self._find(part_id)
        delta = -quantity if kind == MovementKind.OUT else quantity
        if part.quantity + delta < 0:
            raise ValidationError(f"Estoque insuficiente de {part.name}: {part.quantity} disponível(is).")
        movement = StockMovement(part_id=part_id, kind=kind, quantity=quantity, at=self._clock(),
                                 author=author, order_code=order_code, note=note)
        self.history.append(movement)
        return self._replace(part.model_copy(update={"quantity": part.quantity + delta}))

    async def restock(self, part_id: str, quantity: int, author: str, note: str = "") -> Part:
        return self._move(part_id, MovementKind.IN, quantity, author, "", note)

    def apply(self, effects: Iterable[StockEffect], author: str, order_code: str) -> None:
        """Efeitos de estoque de uma gravação de ordem (decisão D2), aplicados como uma unidade."""
        effects = list(effects)
        snapshot = (list(self.items), list(self.history))
        try:
            for effect in effects:
                self._move(effect.part_id, effect.kind, effect.quantity, author, order_code, "")
        except Exception:
            self.items, self.history = snapshot
            raise

    async def movements(self) -> list[StockMovement]:
        return list(reversed(self.history))
