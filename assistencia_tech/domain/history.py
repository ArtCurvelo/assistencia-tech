"""Criação dos eventos do histórico da ordem de serviço.

Eventos são imutáveis e apenas acrescentados ao agregado; não existe
operação de edição ou exclusão de eventos.
"""

from __future__ import annotations

from datetime import datetime

from ..models.entities import HistoryEvent, OrderItem, Payment, ServiceOrder
from .validators import format_brl

KIND_OPENED = "Abertura"
KIND_STATUS = "Status"
KIND_TECHNICIAN = "Técnico"
KIND_DIAGNOSIS = "Diagnóstico"
KIND_ITEM_ADDED = "Item adicionado"
KIND_ITEM_REMOVED = "Item removido"
KIND_PAYMENT = "Pagamento"
KIND_CLIENT_DECISION = "Decisão do cliente"
KIND_DUE_DATE = "Prazo"


def _event(kind: str, description: str, at: datetime, author: str, to_status: str = "") -> HistoryEvent:
    return HistoryEvent(at=at, author=author, kind=kind, description=description, to_status=to_status)


def opened(problem: str, at: datetime, author: str, warranty_of: str = "") -> HistoryEvent:
    prefix = f"Ordem aberta em garantia da {warranty_of}." if warranty_of else "Ordem aberta."
    return _event(KIND_OPENED, f"{prefix} Problema relatado: {problem}", at, author)


def due_date_changed(due, at: datetime, author: str) -> HistoryEvent:
    return _event(KIND_DUE_DATE, f"Previsão de entrega alterada para {due:%d/%m/%Y}.", at, author)


def status_changed(previous: str, new: str, at: datetime, author: str, reason: str = "") -> HistoryEvent:
    text = f"Status alterado de {previous} para {new}."
    if reason:
        text += f" Motivo: {reason}"
    return _event(KIND_STATUS, text, at, author, to_status=str(new))


def client_decision(approved: bool, reason: str, at: datetime, author: str) -> HistoryEvent:
    """Decisão do cliente sobre o orçamento (mesmo texto gravado pelo backend Xano)."""
    if approved:
        return _event(KIND_CLIENT_DECISION, "Orçamento aprovado pelo cliente.", at, author)
    return _event(KIND_CLIENT_DECISION, f"Orçamento recusado pelo cliente. Motivo: {reason}", at, author)


def technician_assigned(name: str, previous: str | None, at: datetime, author: str) -> HistoryEvent:
    text = f"Técnico alterado de {previous} para {name}." if previous else f"Técnico {name} atribuído."
    return _event(KIND_TECHNICIAN, text, at, author)


def diagnosis_recorded(diagnosis: str, at: datetime, author: str) -> HistoryEvent:
    return _event(KIND_DIAGNOSIS, f"Diagnóstico registrado: {diagnosis}", at, author)


def _item_text(item: OrderItem) -> str:
    if item.quantity > 1:
        return f"{item.kind} {item.description} ({item.quantity} × {format_brl(item.unit_price)})"
    return f"{item.kind} {item.description} ({format_brl(item.unit_price)})"


def item_added(item: OrderItem, at: datetime, author: str) -> HistoryEvent:
    return _event(KIND_ITEM_ADDED, f"Adicionado ao orçamento: {_item_text(item)}.", at, author)


def item_removed(item: OrderItem, at: datetime, author: str) -> HistoryEvent:
    return _event(KIND_ITEM_REMOVED, f"Removido do orçamento: {_item_text(item)}.", at, author)


def payment_recorded(payment: Payment, at: datetime, author: str) -> HistoryEvent:
    return _event(KIND_PAYMENT, f"Pagamento de {format_brl(payment.amount)} em {payment.method}.", at, author)


def append(order: ServiceOrder, event: HistoryEvent, **changes: object) -> ServiceOrder:
    """Nova versão da ordem com as alterações e o evento acrescentado."""
    return order.model_copy(update={**changes, "history": (*order.history, event), "updated_at": event.at})
