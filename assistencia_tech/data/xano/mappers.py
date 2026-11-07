"""Conversão entre os registros do Xano e os modelos internos.

Os nomes de campo do Xano são os da documentação publicada (veja
``docs/XANO_BACKEND_SPEC.md``). Datas do Xano chegam como milissegundos desde
1970 (``timestamp``) ou ``AAAA-MM-DD`` (``date``). O código ``OS-AAAA-NNNNN``
é derivado do ano de ``created_at`` e do ``id`` (decisão D13).
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ...domain.clock import BRT
from ...models import (
    EQUIPMENT_KINDS,
    Client,
    ClientCreate,
    Equipment,
    EquipmentCreate,
    HistoryEvent,
    ItemKind,
    OrderItem,
    OrderStatus,
    Payment,
    PublicOrderView,
    Role,
    ServiceOrder,
    Technician,
    UserAccount,
)
from ..errors import NotFoundError, UnexpectedError

logger = logging.getLogger(__name__)

Record = dict[str, Any]

STATUS_TO_XANO: dict[OrderStatus, str] = {
    OrderStatus.RECEIVED: "recebido",
    OrderStatus.ANALYSIS: "em_analise",
    OrderStatus.AWAITING_APPROVAL: "aguardando_aprovacao",
    OrderStatus.REPAIR: "em_reparo",
    OrderStatus.DONE: "concluido",
    OrderStatus.DELIVERED: "entregue",
    OrderStatus.CANCELLED: "cancelado",
}
STATUS_FROM_XANO = {value: status for status, value in STATUS_TO_XANO.items()}

ROLE_TO_XANO: dict[Role, str] = {
    Role.ADMIN: "admin",
    Role.ATTENDANT: "atendente",
    Role.TECHNICIAN: "tecnico",
    Role.CLIENT: "cliente",
}
ROLE_FROM_XANO = {value: role for role, value in ROLE_TO_XANO.items()}

ITEM_TO_XANO: dict[ItemKind, str] = {ItemKind.SERVICE: "servico", ItemKind.PART: "peca"}
ITEM_FROM_XANO = {value: kind for kind, value in ITEM_TO_XANO.items()}

_CODE_RE = re.compile(r"^OS-(\d{4})-(\d+)$")


# ----------------------------------------------------------------------
# Valores
# ----------------------------------------------------------------------
def _id(value: Any) -> str:
    if value in (None, "", 0):
        raise UnexpectedError(detail=f"registro do Xano sem id válido: {value!r}")
    return str(value)


def _optional_id(value: Any) -> str | None:
    return str(value) if value not in (None, "", 0) else None


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def to_datetime(value: Any) -> datetime | None:
    """``timestamp`` do Xano (ms desde 1970) ou texto ISO para ``datetime`` em BRT."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, BRT).replace(microsecond=0)
    if isinstance(value, str):
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=BRT)
        return parsed.astimezone(BRT).replace(microsecond=0)
    raise UnexpectedError(detail=f"data em formato inesperado: {value!r}")


def _required_datetime(value: Any) -> datetime:
    parsed = to_datetime(value)
    if parsed is None:
        raise UnexpectedError(detail="registro do Xano sem created_at")
    return parsed


def to_money(value: Any) -> Decimal:
    return Decimal(f"{float(value):.2f}")


def to_date_text(value: datetime) -> str:
    return value.astimezone(BRT).date().isoformat()


def from_date_text(value: Any, fallback: datetime) -> datetime:
    if isinstance(value, str) and value:
        day = date.fromisoformat(value[:10])
        return datetime(day.year, day.month, day.day, tzinfo=BRT)
    return to_datetime(value) or fallback


# ----------------------------------------------------------------------
# Código da ordem de serviço
# ----------------------------------------------------------------------
def order_code(order_id: Any, created_at: datetime) -> str:
    return f"OS-{created_at.year}-{int(order_id):05d}"


def normalize_order_code(code: str) -> str:
    year, order_id = parse_order_code(code)
    return f"OS-{year}-{order_id:05d}"


def parse_order_code(code: str) -> tuple[int, int]:
    """Retorna ``(ano, id)`` do código ou lança ``NotFoundError``."""
    match = _CODE_RE.match((code or "").strip().upper())
    if not match or int(match.group(2)) <= 0:
        raise NotFoundError(f"Ordem de serviço não encontrada: {(code or '').strip() or '(vazio)'}.")
    return int(match.group(1)), int(match.group(2))


# ----------------------------------------------------------------------
# Contas e técnicos
# ----------------------------------------------------------------------
def role_from(value: Any) -> Role:
    role = ROLE_FROM_XANO.get(_text(value))
    if role is None:
        raise UnexpectedError(detail=f"perfil desconhecido no Xano: {value!r}")
    return role


def user_from(record: Record) -> UserAccount:
    role = role_from(record.get("role"))
    user_id = _id(record.get("id"))
    return UserAccount(
        id=user_id,
        name=_text(record.get("name")) or _text(record.get("email")),
        email=_text(record.get("email")),
        role=role,
        client_id=_optional_id(record.get("cliente_id")),
        # Técnicos são contas com perfil técnico: o id do técnico é o id da conta.
        technician_id=user_id if role == Role.TECHNICIAN else None,
        active=record.get("ativo") is not False,
    )


def technician_from(record: Record) -> Technician:
    return Technician(
        id=_id(record.get("id")),
        name=_text(record.get("name")),
        specialty=_text(record.get("especialidade")),
        active=record.get("ativo") is not False,
    )


# ----------------------------------------------------------------------
# Clientes e equipamentos
# ----------------------------------------------------------------------
def client_from(record: Record) -> Client:
    return Client(
        id=_id(record.get("id")),
        name=_text(record.get("Nome")),
        cpf=_text(record.get("Cpf")),
        email=_text(record.get("email")),
        phone=_text(record.get("telefone_Aparelho")),
    )


def client_payload(data: ClientCreate) -> Record:
    return {"Nome": data.name, "Cpf": data.cpf, "email": data.email, "telefone_Aparelho": data.phone}


def equipment_from(record: Record) -> Equipment:
    kind = _text(record.get("aparelho"))
    if kind not in EQUIPMENT_KINDS:
        logger.warning("Tipo de aparelho fora da lista (%r) exibido como 'Outro'.", kind)
        kind = "Outro"
    return Equipment(
        id=_id(record.get("id")),
        client_id=_id(record.get("cliente_id")),
        kind=kind,
        brand=_text(record.get("marca")),
        model=_text(record.get("modelo")),
        serial_number=_text(record.get("numero_serie")),
        notes=_text(record.get("observacoes")),
    )


def equipment_payload(data: EquipmentCreate) -> Record:
    return {
        "cliente_id": int(data.client_id),
        "aparelho": data.kind,
        "marca": data.brand,
        "modelo": data.model,
        "numero_serie": data.serial_number,
        "observacoes": data.notes,
    }


# ----------------------------------------------------------------------
# Ordem de serviço
# ----------------------------------------------------------------------
def item_from(record: Record) -> OrderItem:
    kind = ITEM_FROM_XANO.get(_text(record.get("tipo")))
    if kind is None:
        raise UnexpectedError(detail=f"tipo de item desconhecido: {record.get('tipo')!r}")
    return OrderItem(
        id=_id(record.get("id")),
        kind=kind,
        description=_text(record.get("descricao")),
        quantity=int(record.get("quantidade") or 1),
        unit_price=to_money(record.get("valor_unitario")),
        part_id=_optional_id(record.get("peca_id")) or "",
    )


def item_payload(order_id: str, item: OrderItem) -> Record:
    payload: Record = {
        "os_servicos_id": int(order_id),
        "tipo": ITEM_TO_XANO[item.kind],
        "descricao": item.description,
        "quantidade": item.quantity,
        "valor_unitario": float(item.unit_price),
    }
    if item.part_id:
        payload["peca_id"] = int(item.part_id)  # o backend dá baixa no estoque na mesma transação
    return payload


def payment_from(record: Record) -> Payment:
    created = to_datetime(record.get("created_at")) or datetime.now(BRT).replace(microsecond=0)
    return Payment(
        id=_id(record.get("id")),
        amount=to_money(record.get("valor_a_ser_pago")),
        method=_text(record.get("forma_de_pagamento")),
        paid_at=from_date_text(record.get("data_do_pagamento"), created),
    )


def payment_payload(order_id: str, payment: Payment) -> Record:
    return {
        "os_servicos_id": int(order_id),
        "valor_a_ser_pago": float(payment.amount),
        "forma_de_pagamento": payment.method,
        "data_do_pagamento": to_date_text(payment.paid_at),
    }


def event_from(record: Record) -> HistoryEvent:
    return HistoryEvent(
        at=_required_datetime(record.get("created_at")),
        author=_text(record.get("autor")) or "Sistema",
        kind=_text(record.get("tipo")) or "Evento",
        description=_text(record.get("descricao")) or "-",
        to_status=_text(record.get("para_status")),
    )


def event_payload(order_id: str, event: HistoryEvent) -> Record:
    return {
        "os_servicos_id": int(order_id),
        "autor": event.author,
        "tipo": event.kind,
        "descricao": event.description,
        "para_status": event.to_status,
    }


def status_from(value: Any) -> OrderStatus:
    status = STATUS_FROM_XANO.get(_text(value))
    if status is None:
        raise UnexpectedError(detail=f"status desconhecido no Xano: {value!r}")
    return status


def _records(value: Any) -> list[Record]:
    return [r for r in value if isinstance(r, dict)] if isinstance(value, list) else []


def to_date(value: Any) -> date | None:
    if isinstance(value, str) and value.strip():
        return date.fromisoformat(value.strip()[:10])
    return None


def _linked_code(record: Any) -> str:
    """Código de uma ordem a partir do resumo (id e created_at) devolvido por um *addon*."""
    if isinstance(record, dict) and record.get("id") and record.get("created_at"):
        return order_code(record["id"], _required_datetime(record["created_at"]))
    return ""


def order_id_of(order: ServiceOrder) -> str:
    return str(parse_order_code(order.code)[1])


def order_from(record: Record) -> ServiceOrder:
    opened = _required_datetime(record.get("created_at"))
    history = tuple(sorted((event_from(r) for r in _records(record.get("_historico"))), key=lambda e: e.at))
    return ServiceOrder(
        code=order_code(_id(record.get("id")), opened),
        client_id=_id(record.get("cliente_id")),
        equipment_id=_id(record.get("item_cliente_id")),
        problem=_text(record.get("descricao_problema")) or "-",
        status=status_from(record.get("status")),
        opened_at=opened,
        updated_at=to_datetime(record.get("atualizado_em")) or opened,
        technician_id=_optional_id(record.get("user_id")),
        diagnosis=_text(record.get("diagnostico")),
        cancel_reason=_text(record.get("motivo_cancelamento")),
        items=tuple(item_from(r) for r in _records(record.get("_itens"))),
        payments=tuple(payment_from(r) for r in _records(record.get("_pagamentos"))),
        history=history,
        due_date=to_date(record.get("previsao_entrega")),
        warranty_of=_linked_code(record.get("_garantia")),
    )


def public_view_from(record: Record) -> PublicOrderView:
    opened = _required_datetime(record.get("created_at"))
    equipment = " ".join(p for p in (_text(record.get("aparelho")), _text(record.get("modelo"))) if p)
    return PublicOrderView(
        code=order_code(_id(record.get("id")), opened),
        status=status_from(record.get("status")).value,
        equipment=equipment or "Equipamento",
        updated_at=to_datetime(record.get("atualizado_em")) or opened,
        due_date=to_date(record.get("previsao_entrega")),
    )
