"""Direitos do titular dos dados (LGPD) no portal do cliente (mudança add-lgpd-portal).

Funções puras: regra de exclusão e montagem do arquivo de exportação. O arquivo
traz apenas dados do próprio cliente e nunca os autores internos do histórico.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from ..data.errors import ValidationError
from ..models.entities import Client, Equipment, OrderStatus, ServiceOrder
from .clock import format_datetime
from .pricing import compute_totals
from .validators import format_brl, format_cpf, format_phone

OPEN_ORDERS_MESSAGE = (
    "Você tem ordens em andamento. A exclusão fica disponível depois que todas forem entregues ou canceladas."
)
EXPORT_FILENAME = "meus-dados-assistencia-tech.json"
_FINAL = (OrderStatus.DELIVERED, OrderStatus.CANCELLED)


def ensure_can_delete(orders: Iterable[ServiceOrder]) -> None:
    if any(order.status not in _FINAL for order in orders):
        raise ValidationError(OPEN_ORDERS_MESSAGE)


def export_data(client: Client, orders: Iterable[tuple[ServiceOrder, Equipment | None]], now: datetime) -> dict:
    """Cadastro, equipamentos, ordens e avaliações do titular, prontos para JSON."""
    pairs = list(orders)
    equipment = {eq.id: eq for _, eq in pairs if eq is not None}
    return {
        "gerado_em": format_datetime(now),
        "base_legal": "LGPD (Lei 13.709/2018), art. 18: acesso e portabilidade dos dados do titular.",
        "cadastro": {"nome": client.name, "cpf": format_cpf(client.cpf), "email": client.email,
                     "telefone": format_phone(client.phone)},
        "equipamentos": [
            {"descricao": eq.description, "tipo": eq.kind, "marca": eq.brand, "modelo": eq.model,
             "numero_de_serie": eq.serial_number}
            for eq in equipment.values()
        ],
        "ordens_de_servico": [_order(order, equipment.get(order.equipment_id)) for order, _ in pairs],
    }


def _order(order: ServiceOrder, equipment: Equipment | None) -> dict:
    totals = compute_totals(order)
    return {
        "codigo": order.code,
        "equipamento": equipment.description if equipment else "",
        "status": order.status.value,
        "aberta_em": format_datetime(order.opened_at),
        "problema_relatado": order.problem,
        "diagnostico": order.diagnosis,
        "previsao_de_entrega": f"{order.due_date:%d/%m/%Y}" if order.due_date else "",
        "itens": [{"tipo": i.kind.value, "descricao": i.description, "quantidade": i.quantity,
                   "valor_unitario": format_brl(i.unit_price)} for i in order.items],
        "total": format_brl(totals.total),
        "pagamentos": [{"data": format_datetime(p.paid_at), "forma": p.method, "valor": format_brl(p.amount)}
                       for p in order.payments],
        # Andamento sem os autores internos (nomes de colaboradores não são dados do titular).
        "andamento": [{"data": format_datetime(e.at), "evento": e.kind, "descricao": e.description}
                      for e in order.history],
        "avaliacao": ({"nota": order.rating.score, "comentario": order.rating.comment,
                       "data": format_datetime(order.rating.at)} if order.rating else None),
    }
