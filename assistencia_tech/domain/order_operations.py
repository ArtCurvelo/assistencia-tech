"""Operações puras sobre o agregado ``ServiceOrder``.

Cada função valida as regras, aplica a alteração e acrescenta o evento ao
histórico, retornando uma nova versão da ordem. Não há I/O: a gravação é
responsabilidade do serviço de aplicação.
"""

from __future__ import annotations

from datetime import datetime

from ..data.errors import NotFoundError, ValidationError
from ..models.entities import (
    ItemKind,
    OrderCreate,
    OrderItem,
    OrderItemCreate,
    OrderStatus,
    Payment,
    PaymentCreate,
    ServiceOrder,
    Technician,
)
from . import deadlines, history
from .order_workflow import (
    check_transition,
    ensure_budget_editable,
    ensure_payment_allowed,
    ensure_technician_changeable,
)


def _next_id(ids: list[str]) -> str:
    return str(max((int(i) for i in ids if i.isdigit()), default=0) + 1)


def open_order(code: str, data: OrderCreate, at: datetime, author: str) -> ServiceOrder:
    due = data.due_date or deadlines.default_due_date(at)
    deadlines.ensure_valid_due_date(due, at)
    return ServiceOrder(
        code=code,
        client_id=data.client_id,
        equipment_id=data.equipment_id,
        problem=data.problem,
        status=OrderStatus.RECEIVED,
        opened_at=at,
        updated_at=at,
        due_date=due,
        warranty_of=data.warranty_of,
        history=(history.opened(data.problem, at, author, data.warranty_of),),
    )


def set_due_date(order: ServiceOrder, due, at: datetime, author: str) -> ServiceOrder:
    deadlines.ensure_due_date_editable(order)
    if due is None:
        raise ValidationError("Informe a nova previsão de entrega.")
    deadlines.ensure_valid_due_date(due, order.opened_at)
    if due == order.due_date:
        raise ValidationError("A previsão informada é igual à atual.")
    return history.append(order, history.due_date_changed(due, at, author), due_date=due)


def assign_technician(
    order: ServiceOrder,
    technician: Technician,
    previous: Technician | None,
    at: datetime,
    author: str,
) -> ServiceOrder:
    ensure_technician_changeable(order)
    if order.technician_id == technician.id:
        raise ValidationError(f"{technician.name} já é o técnico responsável por esta ordem.")
    event = history.technician_assigned(technician.name, previous.name if previous else None, at, author)
    return history.append(order, event, technician_id=technician.id)


def record_diagnosis(order: ServiceOrder, text: str, at: datetime, author: str) -> ServiceOrder:
    ensure_budget_editable(order)
    diagnosis = (text or "").strip()
    if not diagnosis:
        raise ValidationError("Preencha o campo obrigatório: Diagnóstico.")
    if diagnosis == order.diagnosis:
        raise ValidationError("O diagnóstico informado é igual ao já registrado.")
    return history.append(order, history.diagnosis_recorded(diagnosis, at, author), diagnosis=diagnosis)


def add_item(order: ServiceOrder, data: OrderItemCreate, at: datetime, author: str) -> ServiceOrder:
    ensure_budget_editable(order)
    quantity = 1 if data.kind == ItemKind.SERVICE else data.quantity
    item = OrderItem(
        id=_next_id([i.id for i in order.items]),
        kind=data.kind,
        description=data.description,
        quantity=quantity,
        unit_price=data.unit_price,
        part_id=data.part_id if data.kind == ItemKind.PART else "",
    )
    return history.append(order, history.item_added(item, at, author), items=(*order.items, item))


def remove_item(order: ServiceOrder, item_id: str, at: datetime, author: str) -> ServiceOrder:
    ensure_budget_editable(order)
    item = next((i for i in order.items if i.id == item_id), None)
    if item is None:
        raise NotFoundError("Item do orçamento não encontrado.")
    remaining = tuple(i for i in order.items if i.id != item_id)
    return history.append(order, history.item_removed(item, at, author), items=remaining)


def add_payment(order: ServiceOrder, data: PaymentCreate, at: datetime, author: str) -> ServiceOrder:
    ensure_payment_allowed(order, data.amount)
    payment = Payment(
        id=_next_id([p.id for p in order.payments]),
        amount=data.amount,
        method=data.method,
        paid_at=at,
    )
    return history.append(order, history.payment_recorded(payment, at, author), payments=(*order.payments, payment))


NOT_AWAITING_DECISION = "Esta ordem não está aguardando a sua aprovação."
REFUSAL_REASON_REQUIRED = "Informe o motivo da recusa."


def refusal_reason(reason: str) -> str:
    return f"Orçamento recusado pelo cliente: {reason.strip()}"


def client_decision(order: ServiceOrder, approve: bool, reason: str, at: datetime, author: str) -> ServiceOrder:
    """O cliente aprova (→ Em reparo) ou recusa com motivo (→ Cancelado) o orçamento."""
    if order.status != OrderStatus.AWAITING_APPROVAL:
        raise ValidationError(NOT_AWAITING_DECISION)
    reason = (reason or "").strip()
    if not approve and not reason:
        raise ValidationError(REFUSAL_REASON_REQUIRED)
    decided = history.append(order, history.client_decision(approve, reason, at, author))
    if approve:
        return change_status(decided, OrderStatus.REPAIR, at, author)
    return change_status(decided, OrderStatus.CANCELLED, at, author, refusal_reason(reason))


def change_status(
    order: ServiceOrder,
    target: str | OrderStatus,
    at: datetime,
    author: str,
    reason: str = "",
) -> ServiceOrder:
    new_status = check_transition(order, target, reason)
    reason = reason.strip()
    changes: dict[str, object] = {"status": new_status}
    if new_status == OrderStatus.CANCELLED:
        changes["cancel_reason"] = reason
    event = history.status_changed(order.status, new_status, at, author, reason if reason else "")
    return history.append(order, event, **changes)
