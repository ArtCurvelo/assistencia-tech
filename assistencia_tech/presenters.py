"""Conversão de entidades de domínio em dicionários de texto para a interface.

O Reflex trabalha melhor com estruturas simples; aqui todos os valores são
pré-formatados (CPF, telefone, reais, datas) e cada linha recebe uma chave
``search`` normalizada para os filtros.
"""

from __future__ import annotations

import unicodedata
from decimal import Decimal

from .domain.clock import format_datetime
from .domain.order_workflow import BUDGET_EDITABLE, OPEN_STATUSES, TECHNICIAN_LOCKED, allowed_next
from .domain.pricing import compute_totals
from .domain.validators import format_brl, format_cpf, format_phone, only_digits
from .models import Client, Equipment, OrderStatus, ServiceOrder, Technician
from .services.catalog import Catalog

Row = dict[str, str]


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "-".join(plain.lower().split())


def search_key(*parts: str) -> str:
    text = " ".join(parts).casefold()
    return f"{text} {only_digits(text)}"


def matches(row: Row, query: str) -> bool:
    query = query.strip().casefold()
    if not query:
        return True
    haystack = row.get("search", "")
    if query in haystack:
        return True
    # Termos sem letras (CPF, telefone) também casam ignorando a pontuação.
    if not any(ch.isalpha() for ch in query):
        digits = only_digits(query)
        return bool(digits) and digits in haystack
    return False


def status_class(status: str) -> str:
    return f"status-badge status-{slug(status)}"


def client_row(client: Client) -> Row:
    return {
        "id": client.id,
        "name": client.name,
        "cpf": format_cpf(client.cpf),
        "email": client.email,
        "phone": format_phone(client.phone),
        "search": search_key(client.name, client.email, client.cpf, client.phone),
    }


def equipment_row(equipment: Equipment, catalog: Catalog) -> Row:
    client = catalog.clients_by_id.get(equipment.client_id)
    orders = sum(1 for o in catalog.orders if o.equipment_id == equipment.id)
    client_name = client.name if client else "Cliente removido"
    return {
        "id": equipment.id,
        "client_id": equipment.client_id,
        "client": client_name,
        "kind": equipment.kind,
        "brand": equipment.brand,
        "model": equipment.model,
        "serial": equipment.serial_number,
        "serial_display": equipment.serial_number or "—",
        "notes": equipment.notes,
        "description": equipment.description,
        "label": f"{equipment.description} · {equipment.serial_number}" if equipment.serial_number else equipment.description,
        "orders_count": str(orders),
        "search": search_key(client_name, equipment.brand, equipment.model, equipment.serial_number, equipment.kind),
    }


def _name(technician: Technician | None) -> str:
    return technician.name if technician else "Não atribuído"


PAYMENT_NOT_APPLICABLE = "Não se aplica"


def payment_label(order: ServiceOrder, status: str) -> str:
    """Ordens canceladas sem pagamento não têm cobrança pendente."""
    if order.status == OrderStatus.CANCELLED and not order.payments:
        return PAYMENT_NOT_APPLICABLE
    return status


def order_row(order: ServiceOrder, catalog: Catalog) -> Row:
    client = catalog.clients_by_id.get(order.client_id)
    equipment = catalog.equipment_by_id.get(order.equipment_id)
    technician = catalog.technicians_by_id.get(order.technician_id or "")
    totals = compute_totals(order)
    client_name = client.name if client else "Cliente removido"
    equipment_name = equipment.description if equipment else "Equipamento removido"
    return {
        "code": order.code,
        "client_id": order.client_id,
        "client": client_name,
        "equipment_id": order.equipment_id,
        "equipment": equipment_name,
        "problem": order.problem,
        "status": order.status.value,
        "status_class": status_class(order.status),
        "technician_id": order.technician_id or "",
        "technician": _name(technician),
        "total": format_brl(totals.total),
        "balance": format_brl(totals.balance),
        "payment_status": payment_label(order, totals.payment_status),
        "payment_class": f"pay-badge pay-{slug(payment_label(order, totals.payment_status))}",
        "opened_at": format_datetime(order.opened_at),
        "updated_at": format_datetime(order.updated_at),
        "search": search_key(order.code, client_name, equipment_name),
    }


def item_rows(order: ServiceOrder) -> list[Row]:
    return [
        {
            "id": item.id,
            "kind": item.kind.value,
            "description": item.description,
            "quantity": str(item.quantity),
            "unit_price": format_brl(item.unit_price),
            "subtotal": format_brl(item.subtotal),
        }
        for item in order.items
    ]


def payment_rows(order: ServiceOrder) -> list[Row]:
    return [
        {"id": p.id, "paid_at": format_datetime(p.paid_at), "method": p.method, "amount": format_brl(p.amount)}
        for p in order.payments
    ]


def history_rows(order: ServiceOrder) -> list[Row]:
    return [
        {"at": format_datetime(e.at), "author": e.author, "kind": e.kind, "description": e.description}
        for e in order.history
    ]


def totals_row(order: ServiceOrder) -> Row:
    t = compute_totals(order)
    return {
        "services": format_brl(t.services),
        "parts": format_brl(t.parts),
        "total": format_brl(t.total),
        "paid": format_brl(t.paid),
        "balance": format_brl(t.balance),
        "payment_status": t.payment_status,
        "has_balance": "1" if t.balance > 0 else "",
    }


def order_permissions(order: ServiceOrder) -> Row:
    """Flags ("1" ou "") das ações permitidas no status atual."""
    return {
        "budget_editable": "1" if order.status in BUDGET_EDITABLE else "",
        "technician_changeable": "" if order.status in TECHNICIAN_LOCKED else "1",
        "payments_allowed": "1"
        if order.status != OrderStatus.CANCELLED and compute_totals(order).balance > 0
        else "",
    }


def next_statuses(order: ServiceOrder) -> list[str]:
    return [status.value for status in allowed_next(order.status)]


def dashboard_metrics(catalog: Catalog) -> Row:
    receivable = sum(
        (compute_totals(o).balance for o in catalog.orders if o.status != OrderStatus.CANCELLED),
        Decimal("0"),
    )
    return {
        "open": str(sum(1 for o in catalog.orders if o.status in OPEN_STATUSES)),
        "awaiting": str(sum(1 for o in catalog.orders if o.status == OrderStatus.AWAITING_APPROVAL)),
        "ready": str(sum(1 for o in catalog.orders if o.status == OrderStatus.DONE)),
        "receivable": format_brl(receivable),
        "clients": str(len(catalog.clients)),
        "equipment": str(len(catalog.equipment)),
        "orders": str(len(catalog.orders)),
    }


def status_counts(catalog: Catalog) -> list[Row]:
    total = max(len(catalog.orders), 1)
    rows = []
    for status in OrderStatus:
        count = sum(1 for o in catalog.orders if o.status == status)
        rows.append(
            {
                "status": status.value,
                "count": str(count),
                "percent": f"{round(count * 100 / total)}%",
                "status_class": status_class(status),
            }
        )
    return rows
