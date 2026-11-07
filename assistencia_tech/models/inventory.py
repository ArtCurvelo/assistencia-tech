"""Estoque de peças: catálogo e movimentações (mudança add-parts-inventory)."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from pydantic import Field, field_validator

from .entities import Money, Text, _Model


class MovementKind(StrEnum):
    IN = "Entrada"
    OUT = "Saída"
    RETURN = "Devolução"


class StockLevel(StrEnum):
    NORMAL = "Normal"
    LOW = "Baixo"
    OUT = "Esgotado"


class PartCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {
        "code": "Código",
        "name": "Nome",
        "unit_price": "Preço de venda",
        "min_quantity": "Estoque mínimo",
    }

    code: Text
    name: Text
    unit_price: Money
    min_quantity: int = Field(default=0, ge=0)
    active: bool = True

    @field_validator("code")
    @classmethod
    def _code(cls, value: str) -> str:
        return value.upper()

    @field_validator("min_quantity", mode="before")
    @classmethod
    def _min(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip() or "0"
            if not value.isdigit():
                raise ValueError("informe um número inteiro maior ou igual a zero")
            return int(value)
        return value


class Part(PartCreate):
    id: Text
    quantity: int = Field(default=0, ge=0)


class StockMovement(_Model):
    part_id: Text
    kind: MovementKind
    quantity: int = Field(gt=0)
    at: datetime
    author: Text
    order_code: str = ""
    note: str = ""
