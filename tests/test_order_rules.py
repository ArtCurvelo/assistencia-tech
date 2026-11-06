"""Regras puras da ordem de serviço: transições, valores, orçamento e histórico."""

from datetime import datetime
from decimal import Decimal

import pytest

from assistencia_tech.data.errors import NotFoundError, ValidationError
from assistencia_tech.domain import history
from assistencia_tech.domain import order_operations as ops
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.order_workflow import TRANSITIONS, allowed_next, check_transition
from assistencia_tech.domain.pricing import compute_totals
from assistencia_tech.models import (
    ItemKind,
    OrderCreate,
    OrderItemCreate,
    OrderStatus,
    PaymentCreate,
    Technician,
)

S = OrderStatus
AT = datetime(2026, 11, 6, 10, 0, tzinfo=BRT)
WHO = "Teste"
TECH = Technician(id="1", name="Carlos")


def new_order():
    return ops.open_order("OS-2026-00001", OrderCreate(client_id="1", equipment_id="1", problem="Não liga"), AT, WHO)


def item(kind=ItemKind.SERVICE, description="Serviço", price="100", quantity=1):
    return OrderItemCreate(kind=kind, description=description, unit_price=price, quantity=quantity)


def to_status(target):
    """Leva uma ordem nova até ``target`` pelo caminho feliz."""
    order = new_order()
    path = {
        S.RECEIVED: [],
        S.ANALYSIS: [S.ANALYSIS],
        S.AWAITING_APPROVAL: [S.ANALYSIS, S.AWAITING_APPROVAL],
        S.REPAIR: [S.ANALYSIS, S.AWAITING_APPROVAL, S.REPAIR],
        S.DONE: [S.ANALYSIS, S.AWAITING_APPROVAL, S.REPAIR, S.DONE],
    }[target]
    for step in path:
        if step == S.ANALYSIS:
            order = ops.assign_technician(order, TECH, None, AT, WHO)
        if step == S.AWAITING_APPROVAL:
            order = ops.record_diagnosis(order, "Fonte queimada", AT, WHO)
            order = ops.add_item(order, item(), AT, WHO)
        order = ops.change_status(order, step, AT, WHO)
    return order


def test_new_order_starts_received_with_history():
    order = new_order()
    assert order.status == S.RECEIVED
    assert [e.kind for e in order.history] == [history.KIND_OPENED]
    assert order.history[0].author == WHO and order.history[0].at == AT


def test_transition_table_matches_spec():
    assert allowed_next(S.RECEIVED) == (S.ANALYSIS, S.CANCELLED)
    assert allowed_next(S.DONE) == (S.DELIVERED,)
    assert allowed_next(S.CANCELLED) == (S.DELIVERED,)
    assert allowed_next(S.DELIVERED) == ()
    assert set(TRANSITIONS) == set(S)


def test_full_happy_path_to_delivered():
    order = to_status(S.DONE)
    order = ops.add_payment(order, PaymentCreate(amount="100", method="PIX"), AT, WHO)
    order = ops.change_status(order, S.DELIVERED, AT, WHO)
    assert order.status == S.DELIVERED
    assert len([e for e in order.history if e.kind == history.KIND_STATUS]) == 5


def test_skipping_steps_is_rejected_with_options():
    with pytest.raises(ValidationError) as info:
        check_transition(new_order(), S.DONE)
    assert "Transição não permitida" in info.value.user_message
    assert "Em análise, Cancelado" in info.value.user_message


def test_unknown_status_is_rejected():
    with pytest.raises(ValidationError, match="Status inválido"):
        check_transition(new_order(), "Perdido")


def test_delivered_is_final():
    order = to_status(S.DONE)
    order = ops.add_payment(order, PaymentCreate(amount="100", method="PIX"), AT, WHO)
    order = ops.change_status(order, S.DELIVERED, AT, WHO)
    with pytest.raises(ValidationError, match="finalizada"):
        check_transition(order, S.CANCELLED, "x")


def test_analysis_requires_technician():
    with pytest.raises(ValidationError, match="técnico"):
        check_transition(new_order(), S.ANALYSIS)


def test_cancel_received_order_without_technician_is_allowed():
    order = ops.change_status(new_order(), S.CANCELLED, AT, WHO, "Cliente desistiu")
    assert order.status == S.CANCELLED and order.cancel_reason == "Cliente desistiu"
    assert "Motivo: Cliente desistiu" in order.history[-1].description


def test_cancel_requires_reason():
    with pytest.raises(ValidationError, match="motivo"):
        check_transition(new_order(), S.CANCELLED, "   ")


def test_approval_requires_diagnosis_then_items():
    order = to_status(S.ANALYSIS)
    with pytest.raises(ValidationError, match="diagnóstico"):
        check_transition(order, S.AWAITING_APPROVAL)
    order = ops.record_diagnosis(order, "Fonte queimada", AT, WHO)
    with pytest.raises(ValidationError, match="ao menos um item"):
        check_transition(order, S.AWAITING_APPROVAL)


def test_delivery_requires_zero_balance():
    order = to_status(S.DONE)
    with pytest.raises(ValidationError, match="R\\$ 100,00"):
        check_transition(order, S.DELIVERED)


def test_cancelled_order_can_be_delivered_without_payment():
    order = ops.change_status(to_status(S.AWAITING_APPROVAL), S.CANCELLED, AT, WHO, "Não aprovado")
    assert ops.change_status(order, S.DELIVERED, AT, WHO).status == S.DELIVERED


def test_totals_match_spec_example():
    order = to_status(S.ANALYSIS)
    order = ops.add_item(order, item(ItemKind.SERVICE, "Mão de obra", "120,00"), AT, WHO)
    order = ops.add_item(order, item(ItemKind.PART, "Cabo", "45,50", quantity=2), AT, WHO)
    totals = compute_totals(order)
    assert (totals.services, totals.parts, totals.total) == (Decimal("120.00"), Decimal("91.00"), Decimal("211.00"))
    assert totals.payment_status == "Pendente"


def test_partial_and_full_payment():
    order = to_status(S.REPAIR)  # orçamento de R$ 100,00
    order = ops.add_payment(order, PaymentCreate(amount="40", method="Dinheiro"), AT, WHO)
    totals = compute_totals(order)
    assert (totals.paid, totals.balance, totals.payment_status) == (Decimal("40.00"), Decimal("60.00"), "Parcial")
    order = ops.add_payment(order, PaymentCreate(amount="60", method="PIX"), AT, WHO)
    assert compute_totals(order).payment_status == "Pago"
    assert [p.id for p in order.payments] == ["1", "2"]


def test_payment_cannot_exceed_balance():
    order = to_status(S.REPAIR)
    with pytest.raises(ValidationError, match="saldo devedor de R\\$ 100,00"):
        ops.add_payment(order, PaymentCreate(amount="100,01", method="PIX"), AT, WHO)


def test_payment_rejected_on_cancelled_or_empty_order():
    with pytest.raises(ValidationError, match="não possui valores"):
        ops.add_payment(new_order(), PaymentCreate(amount="10", method="PIX"), AT, WHO)
    cancelled = ops.change_status(new_order(), S.CANCELLED, AT, WHO, "x")
    with pytest.raises(ValidationError, match="canceladas"):
        ops.add_payment(cancelled, PaymentCreate(amount="10", method="PIX"), AT, WHO)


def test_service_item_quantity_is_always_one():
    order = ops.add_item(to_status(S.ANALYSIS), item(ItemKind.SERVICE, "Limpeza", "50", quantity=3), AT, WHO)
    assert order.items[-1].quantity == 1


@pytest.mark.parametrize("status", [S.RECEIVED, S.DONE])
def test_budget_locked_outside_editable_statuses(status):
    order = to_status(status)
    with pytest.raises(ValidationError, match="não podem ser alterados"):
        ops.add_item(order, item(), AT, WHO)
    with pytest.raises(ValidationError):
        ops.record_diagnosis(order, "Novo diagnóstico", AT, WHO)


def test_remove_item_and_history():
    order = to_status(S.ANALYSIS)
    order = ops.add_item(order, item(ItemKind.PART, "SSD 480 GB", "250"), AT, WHO)
    order = ops.add_item(order, item(ItemKind.SERVICE, "Instalação", "80"), AT, WHO)
    order = ops.remove_item(order, "1", AT, WHO)
    assert [i.description for i in order.items] == ["Instalação"]
    assert order.history[-1].kind == history.KIND_ITEM_REMOVED
    assert "SSD 480 GB" in order.history[-1].description
    with pytest.raises(NotFoundError):
        ops.remove_item(order, "99", AT, WHO)
    # Novo item não reutiliza o identificador de um item ainda existente.
    assert ops.add_item(order, item(), AT, WHO).items[-1].id == "3"


def test_technician_change_is_recorded_and_locked_after_cancel():
    order = ops.assign_technician(new_order(), TECH, None, AT, WHO)
    other = Technician(id="2", name="Fernanda")
    order = ops.assign_technician(order, other, TECH, AT, WHO)
    assert order.technician_id == "2"
    assert order.history[-1].description == "Técnico alterado de Carlos para Fernanda."
    with pytest.raises(ValidationError, match="já é o técnico"):
        ops.assign_technician(order, other, other, AT, WHO)
    cancelled = ops.change_status(order, S.CANCELLED, AT, WHO, "x")
    with pytest.raises(ValidationError, match="não pode ser alterado"):
        ops.assign_technician(cancelled, TECH, other, AT, WHO)


def test_every_event_kind_has_time_author_and_text():
    order = to_status(S.REPAIR)
    order = ops.add_payment(order, PaymentCreate(amount="10", method="PIX"), AT, WHO)
    kinds = {e.kind for e in order.history}
    assert kinds >= {
        history.KIND_OPENED,
        history.KIND_TECHNICIAN,
        history.KIND_STATUS,
        history.KIND_DIAGNOSIS,
        history.KIND_ITEM_ADDED,
        history.KIND_PAYMENT,
    }
    assert all(e.at == AT and e.author == WHO and e.description for e in order.history)


def test_history_is_immutable():
    order = new_order()
    with pytest.raises(Exception):
        order.history[0].description = "alterado"  # type: ignore[misc]
    with pytest.raises(Exception):
        order.history.append(order.history[0])  # type: ignore[attr-defined]
