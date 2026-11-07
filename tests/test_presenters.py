import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.presenters import (
    client_row,
    dashboard_metrics,
    matches,
    next_statuses,
    order_permissions,
    order_row,
    slug,
    payment_summary,
    status_chart,
    status_counts,
    totals_row,
)
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.services import load_catalog

pytestmark = pytest.mark.anyio


@pytest.fixture
async def catalog():
    admin = Principal("1", "Ana", "admin@assistencia.test", Role.ADMIN)
    return await load_catalog(build_demo_gateway(year_provider=lambda: 2026), admin)


def test_slug_removes_accents():
    assert slug("Aguardando aprovação") == "aguardando-aprovacao"
    assert slug("Não se aplica") == "nao-se-aplica"


async def test_client_row_formats_and_searches(catalog):
    row = client_row(catalog.clients_by_id["1"])
    assert row["cpf"] == "390.533.447-05" and row["phone"] == "(11) 98888-1001"
    assert matches(row, "MARINA")
    assert matches(row, "39053344705") and matches(row, "390.533")
    assert matches(row, "(11) 98888")
    assert not matches(row, "rafael")
    assert matches(row, "   ")


async def test_order_row_and_cancelled_payment_label(catalog):
    by_code = {o.code: o for o in catalog.orders}
    row = order_row(by_code["OS-2026-00122"], catalog)
    assert row["client"] == "Beatriz Lima" and row["equipment"] == "Tablet Apple iPad 9"
    assert (row["total"], row["balance"], row["payment_status"]) == ("R$ 211,00", "R$ 111,00", "Parcial")
    assert row["status_class"] == "status-badge status-concluido"
    cancelled = order_row(by_code["OS-2026-00121"], catalog)
    assert cancelled["payment_status"] == "Não se aplica"
    assert cancelled["payment_class"] == "pay-badge pay-nao-se-aplica"


ADMIN = Principal("1", "Ana", "admin@assistencia.test", Role.ADMIN)
ATTENDANT = Principal("2", "Paulo", "atendimento@assistencia.test", Role.ATTENDANT)
FERNANDA = Principal("4", "Fernanda", "fernanda@assistencia.test", Role.TECHNICIAN, technician_id="2")


async def test_permissions_and_next_statuses(catalog):
    by_code = {o.code: o for o in catalog.orders}
    assert next_statuses(by_code["OS-2026-00126"], ADMIN) == ["Em análise", "Cancelado"]
    assert next_statuses(by_code["OS-2026-00126"], ATTENDANT) == ["Cancelado"]
    assert next_statuses(by_code["OS-2026-00120"], ADMIN) == []
    repair = order_permissions(by_code["OS-2026-00125"], ADMIN)
    assert repair == {"budget_editable": "1", "technician_changeable": "1", "payments_allowed": "1",
                      "read_only_reason": "", "due_editable": "1", "warranty_openable": ""}
    delivered = order_permissions(by_code["OS-2026-00120"], ADMIN)
    assert delivered["budget_editable"] == delivered["technician_changeable"] == delivered["payments_allowed"] == ""
    # Técnica responsável por outra ordem: somente consulta.
    other = order_permissions(by_code["OS-2026-00125"], FERNANDA)
    assert other["budget_editable"] == "" and other["payments_allowed"] == "" and other["read_only_reason"]
    assert next_statuses(by_code["OS-2026-00125"], FERNANDA) == []
    own = order_permissions(by_code["OS-2026-00124"], FERNANDA)
    assert own["budget_editable"] == "1" and own["technician_changeable"] == ""
    assert totals_row(by_code["OS-2026-00120"])["has_balance"] == ""


async def test_dashboard_metrics(catalog):
    metrics = dashboard_metrics(catalog)
    assert metrics["open"] == "5"
    assert metrics["awaiting"] == "1" and metrics["ready"] == "1"
    # 00125: 185,00 + 00123: 410,00 + 00122: 111,00 (canceladas não entram)
    assert metrics["receivable"] == "R$ 706,00"
    counts = {row["status"]: row["count"] for row in status_counts(catalog)}
    assert set(counts.values()) == {"1"} and len(counts) == 7


async def test_chart_data(catalog):
    chart = status_chart(catalog)
    assert [row["status"] for row in chart][0] == "Recebido" and len(chart) == 7
    assert all(row["quantidade"] == 1 for row in chart)
    colors = {row["color"] for row in status_counts(catalog)}
    assert len(colors) == 7 and all(c.startswith("#") for c in colors)
    # Canceladas e ordens sem valor ficam de fora: 00120 pago; 00122 parcial; 00123 e 00125 pendentes.
    summary = {row["situacao"]: row["quantidade"] for row in payment_summary(catalog)}
    assert summary == {"Pendente": 2, "Parcial": 1, "Pago": 1}


async def test_empty_metrics_show_dash_for_every_indicator(catalog):
    from assistencia_tech.presenters import EMPTY_METRICS

    assert set(EMPTY_METRICS) == set(dashboard_metrics(catalog))
    assert set(EMPTY_METRICS.values()) == {"—"}
