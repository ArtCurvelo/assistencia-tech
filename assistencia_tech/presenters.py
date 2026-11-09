"""Conversão de entidades de domínio em dicionários de texto para a interface.

O Reflex trabalha melhor com estruturas simples; aqui todos os valores são
pré-formatados (CPF, telefone, reais, datas) e cada linha recebe uma chave
``search`` normalizada para os filtros.
"""

from __future__ import annotations

import unicodedata
from datetime import timedelta
from decimal import Decimal

from .domain.clock import BRT, format_datetime, now_brt
from .domain import deadlines, rating as rating_rules, receipt
from .domain.inventory import stock_level
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


def deadline_fields(order: ServiceOrder, today=None) -> Row:
    """Previsão, atraso e garantia (add-deadlines-and-warranty)."""
    today = today or now_brt().date()
    late = deadlines.days_late(order, today)
    until = deadlines.warranty_until(order)
    return {
        "due_date": f"{order.due_date:%d/%m/%Y}" if order.due_date else "—",
        "due_input": order.due_date.isoformat() if order.due_date else "",
        "late": (f"Atrasada há {late} dia" + ("s" if late > 1 else "")) if late else "",
        "warranty_until": f"{until:%d/%m/%Y}" if until else "",
        "in_warranty": "1" if until and today <= until else "",
        "warranty_of": order.warranty_of,
    }


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
        **deadline_fields(order),
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
        "due_editable": _flag(
            order.status not in deadlines.FINAL_STATUSES and has_permission(principal, Permission.ORDERS_ASSIGN)
        ),
        "warranty_openable": _flag(
            deadlines.in_warranty(order, now_brt().date()) and has_permission(principal, Permission.ORDERS_OPEN)
        ),
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
    "overdue": "—", "nps": "—", "nps_count": "—", "received_month": "—",
}
NPS_WINDOW_DAYS = 90


def nps_text(value: int | None) -> str:
    return "—" if value is None else (f"+{value}" if value > 0 else str(value))


def average_text(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}".replace(".", ",")


def rating_row(order: ServiceOrder) -> Row:
    """Avaliação do cliente (add-service-rating); vazio quando ainda não há."""
    r = order.rating
    if r is None:
        return {"score": "", "group": "", "group_class": "", "comment": "", "at": ""}
    group = rating_rules.classify(r.score)
    return {"score": str(r.score), "group": group, "group_class": f"rating-badge rating-{slug(group)}",
            "comment": r.comment, "at": format_datetime(r.at)}


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
        "overdue": str(sum(1 for o in catalog.orders if deadlines.is_overdue(o, now_brt().date()))),
        "clients": str(len(catalog.clients)),
        "equipment": str(len(catalog.equipment)),
        "orders": str(len(catalog.orders)),
        "received_month": format_brl(received_in_month(catalog)),
        **_dashboard_nps(catalog),
    }


def _dashboard_nps(catalog: Catalog) -> Row:
    since = now_brt().date() - timedelta(days=NPS_WINDOW_DAYS)
    scores = [o.rating.score for o in catalog.orders if o.rating and o.rating.at.astimezone(BRT).date() >= since]
    summary = rating_rules.nps_summary(scores)
    return {"nps": nps_text(summary.nps), "nps_count": str(summary.count)}


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
        **deadline_fields(order),
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
             "budget": format_brl(row.budget_total), "rating": average_text(row.average_rating)}
            for row in report.technicians
        ],
        "satisfaction": _satisfaction_view(report.satisfaction),
        "comments": [
            {"code": c.code, "score": str(c.score), "comment": c.comment, "at": format_datetime(c.at),
             "group_class": f"rating-badge rating-{slug(rating_rules.classify(c.score))}"}
            for c in report.satisfaction.comments
        ],
    }


def _satisfaction_view(satisfaction) -> Row:
    s = satisfaction.summary
    return {"nps": nps_text(s.nps), "average": average_text(s.average), "count": str(s.count),
            "promoters": str(s.promoters), "neutrals": str(s.neutrals), "detractors": str(s.detractors)}


# ----------------------------------------------------------------------
# Estoque de peças (add-parts-inventory)
# ----------------------------------------------------------------------
def part_row(part) -> Row:
    level = stock_level(part)
    return {
        "id": part.id,
        "code": part.code,
        "name": part.name,
        "price": format_brl(part.unit_price),
        "price_input": f"{part.unit_price:.2f}".replace(".", ","),
        "quantity": str(part.quantity),
        "min_quantity": str(part.min_quantity),
        "level": level.value if part.active else "Inativa",
        "level_class": f"stock-badge stock-{slug(level.value) if part.active else 'inativa'}",
        "active": "sim" if part.active else "nao",
    }


def part_option(part) -> Row:
    return {"value": part.id, "label": f"{part.name} · {format_brl(part.unit_price)} · disp. {part.quantity}"}


def movement_row(movement, parts_by_id: dict) -> Row:
    part = parts_by_id.get(movement.part_id)
    sign = "+" if movement.kind.value != "Saída" else "−"
    return {
        "at": format_datetime(movement.at),
        "part": part.name if part else f"Peça {movement.part_id}",
        "kind": movement.kind.value,
        "kind_class": f"move-badge move-{slug(movement.kind.value)}",
        "quantity": f"{sign}{movement.quantity}",
        "order": movement.order_code,
        "author": movement.author,
        "note": movement.note or "—",
    }


# ----------------------------------------------------------------------
# Comprovante da ordem (add-order-receipt)
# ----------------------------------------------------------------------
def receipt_row(order: ServiceOrder, client: Client | None, equipment: Equipment | None, base_url: str) -> Row:
    """Textos do comprovante: dados mínimos do cliente (CPF mascarado), sem autores nem diagnóstico."""
    url = receipt.tracking_url(base_url, order.code)
    delivered = deadlines.delivered_at(order)
    until = deadlines.warranty_until(order)
    return {
        "kind": receipt.receipt_kind(order),
        "is_delivery": _flag(order.status == OrderStatus.DELIVERED),
        "code": order.code,
        "status": order.status.value,
        "opened_at": format_datetime(order.opened_at),
        "client": client.name if client else "Cliente removido",
        "cpf": mask_cpf(client.cpf) if client else "—",
        "phone": format_phone(client.phone) if client else "—",
        "equipment": equipment.description if equipment else "Equipamento removido",
        "serial": (equipment.serial_number if equipment else "") or "—",
        "problem": order.problem,
        "due_date": f"{order.due_date:%d/%m/%Y}" if order.due_date else "—",
        "cancel_reason": order.cancel_reason if order.status == OrderStatus.CANCELLED else "",
        "warranty_of": order.warranty_of,
        "delivered_at": format_datetime(delivered) if delivered else "",
        "warranty_until": f"{until:%d/%m/%Y}" if until else "",
        "tracking_url": url,
        "qr": receipt.qr_svg_data_uri(url),
    }


# ----------------------------------------------------------------------
# Painel orientado a ações (improve-services-and-dashboard)
# ----------------------------------------------------------------------
ATTENTION_LIMIT = 8
WEEKDAYS = ("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo")
MONTHS = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
          "novembro", "dezembro")


def greeting(name: str, now) -> Row:
    """Saudação pelo horário de Brasília e data por extenso."""
    local = now.astimezone(BRT)
    period = "Bom dia" if local.hour < 12 else "Boa tarde" if local.hour < 18 else "Boa noite"
    first = (name or "").split(" ")[0]
    return {
        "text": f"{period}, {first}!" if first else f"{period}!",
        "date": f"{WEEKDAYS[local.weekday()]}, {local.day} de {MONTHS[local.month - 1]} de {local.year}",
    }


def _attention_row(order: ServiceOrder, catalog: Catalog, reason: str, kind: str) -> Row:
    client = catalog.clients_by_id.get(order.client_id)
    equipment = catalog.equipment_by_id.get(order.equipment_id)
    return {
        "code": order.code,
        "client": client.name if client else "Cliente removido",
        "equipment": equipment.description if equipment else "Equipamento removido",
        "reason": reason,
        "reason_class": f"attention-badge attention-{kind}",
    }


def attention_rows(catalog: Catalog, today=None) -> list[Row]:
    """Atrasadas (mais atraso primeiro), prontas para entrega e aguardando o cliente (mais antigas primeiro)."""
    today = today or now_brt().date()
    rows: list[Row] = []
    seen: set[str] = set()

    def add(orders, reason, kind):
        for order in orders:
            if order.code not in seen:
                seen.add(order.code)
                rows.append(_attention_row(order, catalog, reason(order), kind))

    late = sorted((o for o in catalog.orders if deadlines.is_overdue(o, today)),
                  key=lambda o: (-deadlines.days_late(o, today), o.code))
    add(late, lambda o: deadline_fields(o, today)["late"], "late")
    def oldest_first(status):
        return sorted((o for o in catalog.orders if o.status == status), key=lambda o: (o.updated_at, o.code))

    add(oldest_first(OrderStatus.DONE), lambda o: "Pronta para entrega", "ready")
    add(oldest_first(OrderStatus.AWAITING_APPROVAL), lambda o: "Aguardando o cliente", "awaiting")
    return rows


def technician_queue(catalog: Catalog, principal: Principal | None) -> list[Row]:
    """Ordens em aberto do técnico logado, mais antigas primeiro (vazio para os demais perfis)."""
    if principal is None or not principal.technician_id:
        return []
    mine = sorted((o for o in catalog.orders
                   if o.technician_id == principal.technician_id and o.status in OPEN_STATUSES),
                  key=lambda o: (o.opened_at, o.code))
    return [order_row(o, catalog) for o in mine]


def received_in_month(catalog: Catalog, today=None) -> Decimal:
    today = today or now_brt().date()
    total = Decimal("0")
    for order in catalog.orders:
        for payment in order.payments:
            paid = payment.paid_at.astimezone(BRT).date()
            if (paid.year, paid.month) == (today.year, today.month):
                total += payment.amount
    return total
