"""Status da ordem de serviço: transições permitidas e pré-condições.

As regras são dados (``TRANSITIONS``) e funções puras. ``check_transition``
lança ``ValidationError`` com a mensagem a exibir ao usuário.
"""

from __future__ import annotations

from ..data.errors import ValidationError
from ..models.entities import ORDER_STATUSES, OrderStatus, ServiceOrder
from .pricing import compute_totals
from .validators import format_brl

S = OrderStatus

TRANSITIONS: dict[OrderStatus, tuple[OrderStatus, ...]] = {
    S.RECEIVED: (S.ANALYSIS, S.CANCELLED),
    S.ANALYSIS: (S.AWAITING_APPROVAL, S.CANCELLED),
    S.AWAITING_APPROVAL: (S.REPAIR, S.CANCELLED),
    S.REPAIR: (S.DONE, S.CANCELLED),
    S.DONE: (S.DELIVERED,),
    S.CANCELLED: (S.DELIVERED,),
    S.DELIVERED: (),
}

# Status em que diagnóstico e orçamento podem ser alterados.
BUDGET_EDITABLE: frozenset[OrderStatus] = frozenset({S.ANALYSIS, S.AWAITING_APPROVAL, S.REPAIR})
# Status em que o técnico não pode mais ser trocado.
TECHNICIAN_LOCKED: frozenset[OrderStatus] = frozenset({S.DELIVERED, S.CANCELLED})
# Status que contam como "em aberto" nos indicadores.
OPEN_STATUSES: frozenset[OrderStatus] = frozenset(
    {S.RECEIVED, S.ANALYSIS, S.AWAITING_APPROVAL, S.REPAIR, S.DONE}
)


def parse_status(value: str | OrderStatus) -> OrderStatus:
    try:
        return OrderStatus(value)
    except ValueError as exc:
        raise ValidationError(f"Status inválido: {value}. Use: {', '.join(ORDER_STATUSES)}.") from exc


def allowed_next(status: OrderStatus) -> tuple[OrderStatus, ...]:
    return TRANSITIONS[status]


def _precondition_error(order: ServiceOrder, target: OrderStatus, reason: str) -> str | None:
    if target == S.ANALYSIS and not order.technician_id:
        return "Atribua um técnico responsável antes de iniciar a análise."
    if target == S.AWAITING_APPROVAL:
        if not order.diagnosis.strip():
            return "Registre o diagnóstico técnico antes de enviar para aprovação."
        if not order.items:
            return "O orçamento precisa ter ao menos um item antes de ser enviado para aprovação."
    if target == S.DELIVERED and order.status == S.DONE:
        balance = compute_totals(order).balance
        if balance > 0:
            return f"Há saldo a receber de {format_brl(balance)}. Registre o pagamento antes da entrega."
    if target == S.CANCELLED and not reason.strip():
        return "Informe o motivo do cancelamento."
    return None


def check_transition(order: ServiceOrder, target: str | OrderStatus, reason: str = "") -> OrderStatus:
    """Valida a mudança de status e retorna o status de destino."""
    target_status = parse_status(target)
    if order.status == S.DELIVERED:
        raise ValidationError("A ordem já foi entregue e está finalizada; o status não pode mais ser alterado.")
    options = allowed_next(order.status)
    if target_status not in options:
        possible = ", ".join(options)
        raise ValidationError(
            f"Transição não permitida: {order.status} → {target_status}. Próximos status possíveis: {possible}."
        )
    error = _precondition_error(order, target_status, reason)
    if error:
        raise ValidationError(error)
    return target_status


def ensure_budget_editable(order: ServiceOrder) -> None:
    if order.status not in BUDGET_EDITABLE:
        raise ValidationError(
            f"O diagnóstico e o orçamento não podem ser alterados com a ordem em {order.status}. "
            "Alterações são permitidas em Em análise, Aguardando aprovação e Em reparo."
        )


def ensure_technician_changeable(order: ServiceOrder) -> None:
    if order.status in TECHNICIAN_LOCKED:
        raise ValidationError(f"O técnico não pode ser alterado com a ordem em {order.status}.")


def ensure_payment_allowed(order: ServiceOrder, amount) -> None:
    if order.status == S.CANCELLED:
        raise ValidationError("Não é possível registrar pagamentos em ordens canceladas.")
    totals = compute_totals(order)
    if totals.total <= 0:
        raise ValidationError("A ordem não possui valores no orçamento para receber pagamento.")
    if amount > totals.balance:
        raise ValidationError(
            f"O pagamento de {format_brl(amount)} excede o saldo devedor de {format_brl(totals.balance)}."
        )
