"""Cálculo dos valores de uma ordem de serviço."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ..models.entities import ItemKind, ServiceOrder
from .validators import quantize

PAYMENT_PENDING = "Pendente"
PAYMENT_PARTIAL = "Parcial"
PAYMENT_PAID = "Pago"
PAYMENT_WARRANTY = "Garantia"

ZERO = Decimal("0.00")


@dataclass(frozen=True)
class OrderTotals:
    services: Decimal
    parts: Decimal
    total: Decimal
    paid: Decimal
    balance: Decimal
    payment_status: str


def payment_status(total: Decimal, paid: Decimal) -> str:
    if paid <= 0:
        return PAYMENT_PENDING
    if paid < total:
        return PAYMENT_PARTIAL
    return PAYMENT_PAID


def compute_totals(order: ServiceOrder) -> OrderTotals:
    services = quantize(sum((i.subtotal for i in order.items if i.kind == ItemKind.SERVICE), ZERO))
    parts = quantize(sum((i.subtotal for i in order.items if i.kind == ItemKind.PART), ZERO))
    total = quantize(services + parts)
    paid = quantize(sum((p.amount for p in order.payments), ZERO))
    if order.warranty_of:
        # Ordem em garantia: o orçamento registra o que foi feito, mas nada é cobrado (D3).
        return OrderTotals(services, parts, ZERO, paid, ZERO, PAYMENT_WARRANTY)
    balance = quantize(max(total - paid, ZERO))
    return OrderTotals(services, parts, total, paid, balance, payment_status(total, paid))
