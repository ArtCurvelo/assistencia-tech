"""Conversão de entidades de domínio em dicionários de texto para a interface.

O Reflex trabalha melhor com estruturas simples; aqui todos os valores são
pré-formatados (CPF, telefone, reais, datas) e cada linha recebe uma chave
``search`` normalizada para os filtros.
"""

from __future__ import annotations

import unicodedata
from decimal import Decimal

from .domain.clock import format_datetime
from .domain.history import KIND_CLIENT_DECISION, KIND_OPENED, KIND_STATUS
from .domain.order_workflow import BUDGET_EDITABLE, OPEN_STATUSES, TECHNICIAN_LOCKED
from .domain.permissions import Permission, Principal, has_permission, is_own_order, transitions_for
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


def _flag(value: bool) -> str:
    return "1" if value else ""


def order_permissions(order: ServiceOrder, principal: Principal | None) -> Row:
    """Flags ("1" ou "") das ações permitidas no status atual para este usuário."""
    own = principal is not None and is_own_order(principal, order)
    return {
        "budget_editable": _flag(
            order.status in BUDGET_EDITABLE and own and has_permission(principal, Permission.ORDERS_DIAGNOSE)
        ),
        "technician_changeable": _flag(
            order.status not in TECHNICIAN_LOCKED and has_permission(principal, Permission.ORDERS_ASSIGN)
        ),
        "payments_allowed": _flag(
            order.status != OrderStatus.CANCELLED
            and compute_totals(order).balance > 0
            and has_permission(principal, Permission.ORDERS_PAYMENTS)
        ),
        "read_only_reason": "" if own else "Esta ordem pertence a outro técnico; você pode apenas consultá-la.",
    }


def next_statuses(order: ServiceOrder, principal: Principal | None) -> list[str]:
    return [status.value for status in transitions_for(principal, order)]


# Cores sólidas dos gráficos (versões opacas das cores dos badges).
STATUS_COLORS: dict[str, str] = {
    "Recebido": "#087cff",
    "Em análise": "#ffbe46",
    "Aguardando aprovação": "#a064ff",
    "Em reparo": "#39ff5a",
    "Concluído": "#25a7ff",
    "Entregue": "#91a4ba",
    "Cancelado": "#ff5c5c",
}
PAYMENT_COLORS: dict[str, str] = {"Pendente": "#ffbe46", "Parcial": "#25a7ff", "Pago": "#39ff5a"}

EMPTY_METRICS: Row = {
    "open": "—", "awaiting": "—", "ready": "—", "receivable": "—", "clients": "—", "equipment": "—", "orders": "—",
}


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
                "color": STATUS_COLORS[status.value],
            }
        )
    return rows


def status_chart(catalog: Catalog) -> list[dict]:
    """Dados do gráfico de barras (quantidade numérica para o Recharts)."""
    return [
        {"status": status.value, "quantidade": sum(1 for o in catalog.orders if o.status == status)}
        for status in OrderStatus
    ]


def payment_summary(catalog: Catalog) -> list[dict]:
    """Situação dos pagamentos das ordens com valor, exceto as canceladas."""
    counts = dict.fromkeys(PAYMENT_COLORS, 0)
    for order in catalog.orders:
        totals = compute_totals(order)
        if order.status != OrderStatus.CANCELLED and totals.total > 0:
            counts[totals.payment_status] += 1
    return [{"situacao": name, "quantidade": count, "fill": PAYMENT_COLORS[name]} for name, count in counts.items()]


# ----------------------------------------------------------------------
# Portal do cliente (sem autores, técnicos ou dados internos)
# ----------------------------------------------------------------------
def mask_cpf(cpf: str) -> str:
    digits = only_digits(cpf)
    return f"***.***.***-{digits[-2:]}" if len(digits) == 11 else "***"


def account_row(client: Client) -> Row:
    return {
        "name": client.name,
        "email": client.email,
        "cpf": mask_cpf(client.cpf),
        "phone": format_phone(client.phone),
    }


def portal_order_row(order: ServiceOrder, equipment: Equipment | None) -> Row:
    totals = compute_totals(order)
    payment = payment_label(order, totals.payment_status)
    return {
        "code": order.code,
        "equipment": equipment.description if equipment else "Equipamento",
        "problem": order.problem,
        "diagnosis": order.diagnosis,
        "status": order.status.value,
        "status_class": status_class(order.status),
        "opened_at": format_datetime(order.opened_at),
        "updated_at": format_datetime(order.updated_at),
        "total": format_brl(totals.total),
        "balance": format_brl(totals.balance),
        "payment_status": payment,
        "payment_class": f"pay-badge pay-{slug(payment)}",
    }


def portal_timeline(order: ServiceOrder) -> list[Row]:
    """Aberturas, mudanças de status e decisões do cliente, sem autor."""
    return [
        {"at": format_datetime(e.at), "description": e.description.split(" Problema relatado:")[0]}
        for e in reversed(order.history)
        if e.kind in (KIND_OPENED, KIND_STATUS, KIND_CLIENT_DECISION)
    ]


# ----------------------------------------------------------------------
# Colaboradores e relatórios
# ----------------------------------------------------------------------
def staff_row(user, technician, actor_id: str) -> Row:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "specialty": technician.specialty if technician else "",
        "specialty_display": technician.specialty if technician else "—",
        "status": "Ativo" if user.active else "Inativo",
        "status_class": "pay-badge pay-pago" if user.active else "pay-badge pay-nao-se-aplica",
        "active": "1" if user.active else "",
        "is_self": "1" if user.id == actor_id else "",
    }


def report_view(report) -> dict:
    """Converte ``OperationalReport`` em textos e listas para a interface."""
    v, r, t = report.volume, report.revenue, report.turnaround
    return {
        "summary": {
            "opened": str(v.opened),
            "delivered": str(v.delivered),
            "cancelled": str(v.cancelled),
            "in_progress": str(v.in_progress),
            "received": format_brl(r.total),
            "ticket": format_brl(r.average_ticket) if r.average_ticket is not None else "—",
            "delivered_count": str(r.delivered_count),
            "turnaround": f"{t.average_days:.1f}".replace(".", ",") + " dias" if t.average_days is not None else "—",
            "turnaround_count": str(t.count),
        },
        "methods": [{"method": m, "amount": format_brl(a)} for m, a in r.by_method.items()],
        "technicians": [
            {"name": row.name, "assigned": str(row.assigned), "finished": str(row.finished),
             "budget": format_brl(row.budget_total)}
            for row in report.technicians
        ],
    }
