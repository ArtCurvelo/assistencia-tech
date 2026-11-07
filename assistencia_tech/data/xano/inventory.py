"""Estoque de peças no Xano (mudança add-parts-inventory).

As baixas e devoluções causadas pelos itens das ordens acontecem no próprio
backend (``os_itens``, ``os_servicos`` e ``portal/decisao_orcamento``), em
transação; aqui ficam o catálogo, a entrada e a consulta das movimentações.
"""

from __future__ import annotations

from typing import Any

from ...models import MovementKind, Part, PartCreate, StockMovement
from ..errors import NotFoundError, UnexpectedError
from . import mappers
from .base import XanoRepository, numeric_id

KIND_FROM_XANO = {"entrada": MovementKind.IN, "saida": MovementKind.OUT, "devolucao": MovementKind.RETURN}


def part_from(record: dict[str, Any]) -> Part:
    return Part(
        id=mappers._id(record.get("id")),
        code=mappers._text(record.get("codigo")),
        name=mappers._text(record.get("nome")),
        unit_price=mappers.to_money(record.get("preco")),
        quantity=int(record.get("quantidade") or 0),
        min_quantity=int(record.get("estoque_minimo") or 0),
        active=record.get("ativo") is not False,
    )


def part_payload(data: PartCreate) -> dict[str, Any]:
    return {
        "codigo": data.code,
        "nome": data.name,
        "preco": float(data.unit_price),
        "estoque_minimo": data.min_quantity,
        "ativo": data.active,
    }


def movement_from(record: dict[str, Any]) -> StockMovement:
    kind = KIND_FROM_XANO.get(mappers._text(record.get("tipo")))
    if kind is None:
        raise UnexpectedError(detail=f"tipo de movimentação desconhecido: {record.get('tipo')!r}")
    order = record.get("_ordem")
    code = ""
    if isinstance(order, dict) and order.get("id") and order.get("created_at"):
        code = mappers.order_code(order["id"], mappers.to_datetime(order["created_at"]))
    return StockMovement(
        part_id=mappers._id(record.get("peca_id")),
        kind=kind,
        quantity=int(record.get("quantidade") or 0),
        at=mappers._required_datetime(record.get("created_at")),
        author=mappers._text(record.get("autor")) or "Sistema",
        order_code=code,
        note=mappers._text(record.get("observacao")),
    )


class XanoPartRepository(XanoRepository):
    async def list(self) -> list[Part]:
        parts = [part_from(r) for r in await self._list("parts.list")]
        return sorted(parts, key=lambda p: p.name.casefold())

    async def get(self, part_id: str) -> Part:
        wanted = str(numeric_id(part_id, "Peça"))
        for part in await self.list():
            if part.id == wanted:
                return part
        raise NotFoundError("Peça não encontrada.")

    async def create(self, data: PartCreate) -> Part:
        return part_from(await self._record("parts.create", json=part_payload(data)))

    async def update(self, part: Part) -> Part:
        pid = numeric_id(part.id, "Peça")
        return part_from(await self._record("parts.update", path_params={"peca_id": pid}, json=part_payload(part)))

    async def restock(self, part_id: str, quantity: int, author: str, note: str = "") -> Part:
        payload = {"peca_id": numeric_id(part_id, "Peça"), "quantidade": quantity, "observacao": note}
        return part_from(await self._record("parts.restock", json=payload))

    async def movements(self) -> list[StockMovement]:
        moves = [movement_from(r) for r in await self._list("parts.movements")]
        return sorted(moves, key=lambda m: m.at, reverse=True)
