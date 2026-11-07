"""Prazos e garantia (mudança add-deadlines-and-warranty)."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import PermissionDeniedError, ValidationError
from assistencia_tech.data.xano import mappers
from assistencia_tech.domain import deadlines
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.domain.pricing import PAYMENT_WARRANTY, compute_totals
from assistencia_tech.models import OrderStatus
from assistencia_tech.presenters import deadline_fields
from assistencia_tech.services import OrderService

pytestmark = pytest.mark.anyio

AT = datetime(2026, 11, 10, 9, 0, tzinfo=BRT)
TODAY = AT.date()
ADMIN = Principal("1", "Ana", "a@x.test", Role.ADMIN)
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)
TECH = Principal("3", "Carlos", "c@x.test", Role.TECHNICIAN, technician_id="1")
DELIVERED = "OS-2026-00120"  # concluída e entregue no seed (cliente 3, equipamento 3)
CANCELLED = "OS-2026-00121"
REPAIR = "OS-2026-00125"


def service(principal=ATTENDANT, gateway=None, now=AT):
    return OrderService(gateway or build_demo_gateway(lambda: 2026), principal, clock=lambda: now)


async def order(code):
    return await build_demo_gateway(lambda: 2026).orders.get_by_code(code)


# ----------------------------------------------------------------------
# Domínio
# ----------------------------------------------------------------------
async def test_overdue_only_before_conclusion():
    repair = (await order(REPAIR)).model_copy(update={"due_date": TODAY - timedelta(days=3)})
    assert deadlines.days_late(repair, TODAY) == 3 and deadlines.is_overdue(repair, TODAY)
    assert deadline_fields(repair, TODAY)["late"] == "Atrasada há 3 dias"
    done = repair.model_copy(update={"status": OrderStatus.DONE})
    assert not deadlines.is_overdue(done, TODAY)
    on_time = repair.model_copy(update={"due_date": TODAY})
    assert not deadlines.is_overdue(on_time, TODAY)


async def test_warranty_is_90_days_after_a_concluded_delivery():
    delivered = await order(DELIVERED)
    until = deadlines.warranty_until(delivered)
    assert until == deadlines.delivered_at(delivered).astimezone(BRT).date() + timedelta(days=90)
    assert deadline_fields(delivered, TODAY)["warranty_until"] == f"{until:%d/%m/%Y}"
    cancelled = await order(CANCELLED)
    delivered_cancelled = cancelled.model_copy(update={"status": OrderStatus.DELIVERED})
    assert deadlines.warranty_until(delivered_cancelled) is None  # cancelada não passou por Concluído


async def test_warranty_eligibility():
    delivered = await order(DELIVERED)
    until = deadlines.warranty_until(delivered)
    deadlines.ensure_warranty_eligible(delivered, delivered.client_id, delivered.equipment_id, until)
    with pytest.raises(ValidationError, match="terminou"):
        deadlines.ensure_warranty_eligible(delivered, delivered.client_id, delivered.equipment_id,
                                           until + timedelta(days=1))
    with pytest.raises(ValidationError, match="mesmo cliente e equipamento"):
        deadlines.ensure_warranty_eligible(delivered, "999", delivered.equipment_id, TODAY)
    with pytest.raises(ValidationError, match="não tem garantia"):
        deadlines.ensure_warranty_eligible(await order(REPAIR), "1", "1", TODAY)


async def test_warranty_order_has_nothing_to_pay():
    repair = (await order(REPAIR)).model_copy(update={"warranty_of": DELIVERED})
    totals = compute_totals(repair)
    assert totals.parts > 0 and totals.total == Decimal("0.00") and totals.balance == Decimal("0.00")
    assert totals.payment_status == PAYMENT_WARRANTY


# ----------------------------------------------------------------------
# Serviço sobre a demonstração
# ----------------------------------------------------------------------
FORM = {"client_id": "1", "equipment_id": "1", "problem": "Tela piscando"}


async def test_default_due_date_is_seven_days():
    created = await service().open(FORM)
    assert created.due_date == date(2026, 11, 17)


async def test_due_date_before_opening_is_refused():
    with pytest.raises(ValidationError, match="anterior à data de abertura"):
        await service().open({**FORM, "due_date": "2026-11-01"})
    created = await service().open({**FORM, "due_date": "20/11/2026"})
    assert created.due_date == date(2026, 11, 20)


async def test_warranty_link_cannot_be_forged_on_open():
    created = await service().open({**FORM, "warranty_of": DELIVERED})
    assert created.warranty_of == ""


async def test_change_due_date_with_history():
    gateway = build_demo_gateway(lambda: 2026)
    updated = await service(gateway=gateway).set_due_date(REPAIR, "2026-11-20")
    assert updated.due_date == date(2026, 11, 20)
    assert updated.history[-1].description == "Previsão de entrega alterada para 20/11/2026."
    with pytest.raises(PermissionDeniedError):
        await service(TECH, gateway).set_due_date(REPAIR, "2026-11-21")
    with pytest.raises(ValidationError, match="não pode ser alterada"):
        await service(gateway=gateway).set_due_date(DELIVERED, "2026-11-21")


async def test_open_warranty_links_the_original():
    gateway = build_demo_gateway(lambda: 2026)
    original = await gateway.orders.get_by_code(DELIVERED)
    created = await service(gateway=gateway).open_warranty(DELIVERED, {"problem": "Voltou a falhar"})
    assert created.warranty_of == DELIVERED
    assert (created.client_id, created.equipment_id) == (original.client_id, original.equipment_id)
    assert created.history[0].description.startswith(f"Ordem aberta em garantia da {DELIVERED}.")


async def test_open_warranty_after_expiry_is_refused():
    original = await order(DELIVERED)
    late = datetime.combine(deadlines.warranty_until(original) + timedelta(days=1), datetime.min.time(), BRT)
    with pytest.raises(ValidationError, match="terminou"):
        await service(now=late).open_warranty(DELIVERED, {"problem": "Voltou"})


async def test_open_warranty_requires_permission():
    with pytest.raises(PermissionDeniedError):
        await service(TECH).open_warranty(DELIVERED, {"problem": "Voltou"})


# ----------------------------------------------------------------------
# Xano
# ----------------------------------------------------------------------
def test_xano_mapping_of_due_date_and_warranty():
    created = int(datetime(2026, 11, 7, 10, 0, tzinfo=BRT).timestamp() * 1000)
    record = {"id": 9, "created_at": created, "atualizado_em": created, "cliente_id": 2, "item_cliente_id": 1,
              "user_id": 0, "descricao_problema": "Voltou", "status": "recebido", "previsao_entrega": "2026-11-14",
              "garantia_de": 1, "_garantia": {"id": 1, "created_at": created},
              "_itens": [], "_pagamentos": [], "_historico": []}
    mapped = mappers.order_from(record)
    assert mapped.due_date == date(2026, 11, 14) and mapped.warranty_of == "OS-2026-00001"
    view = mappers.public_view_from({"id": 9, "created_at": created, "status": "recebido",
                                     "previsao_entrega": "2026-11-14", "aparelho": "Notebook", "modelo": "X"})
    assert view.due_date == date(2026, 11, 14)
