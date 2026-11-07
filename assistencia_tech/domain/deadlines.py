"""Prazos e garantia das ordens de serviço (mudança add-deadlines-and-warranty).

Funções puras: recebem a data de hoje. A data da entrega vem do histórico
(evento de status para "Entregue"), que é imutável.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from ..data.errors import ValidationError
from ..models.entities import OrderStatus, ServiceOrder
from .clock import BRT

DEFAULT_LEAD_DAYS = 7
WARRANTY_DAYS = 90  # CDC, art. 26, II: serviços e produtos duráveis

S = OrderStatus
# Antes de "Concluído": ordens que ainda podem atrasar.
PENDING_STATUSES = frozenset({S.RECEIVED, S.ANALYSIS, S.AWAITING_APPROVAL, S.REPAIR})
FINAL_STATUSES = frozenset({S.DELIVERED, S.CANCELLED})


def default_due_date(opened_at: datetime) -> date:
    return opened_at.astimezone(BRT).date() + timedelta(days=DEFAULT_LEAD_DAYS)


def ensure_valid_due_date(due: date, opened_at: datetime) -> None:
    if due < opened_at.astimezone(BRT).date():
        raise ValidationError("A previsão de entrega não pode ser anterior à data de abertura.")


def days_late(order: ServiceOrder, today: date) -> int:
    if order.status not in PENDING_STATUSES or order.due_date is None:
        return 0
    return max((today - order.due_date).days, 0)


def is_overdue(order: ServiceOrder, today: date) -> bool:
    return days_late(order, today) > 0


def delivered_at(order: ServiceOrder) -> datetime | None:
    for event in reversed(order.history):
        if event.to_status == S.DELIVERED.value:
            return event.at
    return None


def warranty_until(order: ServiceOrder) -> date | None:
    """Garantia de 90 dias após a entrega de uma ordem que passou por "Concluído"."""
    if order.status != S.DELIVERED:
        return None
    concluded = any(event.to_status == S.DONE.value for event in order.history)
    delivered = delivered_at(order)
    if not concluded or delivered is None:
        return None
    return delivered.astimezone(BRT).date() + timedelta(days=WARRANTY_DAYS)


def in_warranty(order: ServiceOrder, today: date) -> bool:
    until = warranty_until(order)
    return until is not None and today <= until


def ensure_warranty_eligible(original: ServiceOrder, client_id: str, equipment_id: str, today: date) -> None:
    until = warranty_until(original)
    if until is None:
        raise ValidationError(f"A ordem {original.code} não tem garantia: só ordens concluídas e entregues têm.")
    if today > until:
        raise ValidationError(f"A garantia da ordem {original.code} terminou em {until:%d/%m/%Y}.")
    if original.client_id != client_id or original.equipment_id != equipment_id:
        raise ValidationError("A ordem em garantia deve ser do mesmo cliente e equipamento da ordem original.")


def ensure_due_date_editable(order: ServiceOrder) -> None:
    if order.status in FINAL_STATUSES:
        raise ValidationError(f"A previsão de entrega não pode ser alterada com a ordem {order.status}.")
