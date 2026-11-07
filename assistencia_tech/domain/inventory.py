"""Regras do estoque de peças (funções puras).

``stock_effects`` calcula quanto cada peça do catálogo deve variar quando uma
ordem passa de uma versão para outra: inclusão de item dá baixa, remoção
devolve e cancelamento devolve todas as peças ainda no orçamento (decisão D2
de ``add-parts-inventory``). O modo demonstração aplica esses efeitos ao gravar
a ordem; o backend Xano aplica os mesmos efeitos nos endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..data.errors import ValidationError
from ..models.entities import OrderStatus, ServiceOrder
from ..models.inventory import MovementKind, Part, StockLevel


@dataclass(frozen=True)
class StockEffect:
    part_id: str
    kind: MovementKind  # Saída (baixa) ou Devolução
    quantity: int


def stock_level(part: Part) -> StockLevel:
    if part.quantity <= 0:
        return StockLevel.OUT
    if part.quantity <= part.min_quantity:
        return StockLevel.LOW
    return StockLevel.NORMAL


def needs_restock(part: Part) -> bool:
    return part.active and stock_level(part) != StockLevel.NORMAL


def ensure_available(part: Part, quantity: int) -> None:
    if not part.active:
        raise ValidationError(f"A peça {part.name} está inativa e não pode ser usada em orçamentos.")
    if quantity > part.quantity:
        unit = "unidade disponível" if part.quantity == 1 else "unidades disponíveis"
        raise ValidationError(f"Estoque insuficiente de {part.name}: {part.quantity} {unit}.")


def stock_effects(before: ServiceOrder | None, after: ServiceOrder) -> list[StockEffect]:
    """Efeitos de estoque da mudança ``before`` → ``after`` (``before`` é ``None`` na abertura)."""
    old = {i.id: i for i in (before.items if before else ()) if i.part_id}
    new = {i.id: i for i in after.items if i.part_id}
    effects = [StockEffect(i.part_id, MovementKind.OUT, i.quantity) for item_id, i in new.items() if item_id not in old]
    effects += [StockEffect(i.part_id, MovementKind.RETURN, i.quantity) for item_id, i in old.items() if item_id not in new]
    was_cancelled = before is not None and before.status == OrderStatus.CANCELLED
    if after.status == OrderStatus.CANCELLED and not was_cancelled:
        effects += [StockEffect(i.part_id, MovementKind.RETURN, i.quantity) for i in new.values()]
    return effects
