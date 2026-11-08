"""Avaliação do atendimento e NPS (mudança add-service-rating)."""

import json
from datetime import date, datetime

import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import NotFoundError, PermissionDeniedError, ValidationError
from assistencia_tech.data.request_context import use_backend_token
from assistencia_tech.data.xano import XanoClient, build_xano_gateway, mappers
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache
from assistencia_tech.domain import rating
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Permission, Principal, Role, has_permission
from assistencia_tech.domain.reports import Period, build_report
from assistencia_tech.models import OrderStatus, Rating
from assistencia_tech.services import PortalService

pytestmark = pytest.mark.anyio

AT = datetime(2026, 11, 8, 10, 0, tzinfo=BRT)
DELIVERED = "OS-2026-00120"  # entregue à cliente 3; já avaliada no seed (nota 9)
REPAIR = "OS-2026-00125"  # em reparo, cliente 1
CLIENT_3 = Principal("30", "Camila Souza", "camila@exemplo.test", Role.CLIENT, client_id="3")
CLIENT_1 = Principal("6", "Marina Oliveira", "marina@example.test", Role.CLIENT, client_id="1")


async def unrated_delivered_gateway():
    """Demonstração com a OS-2026-00120 entregue e ainda sem avaliação."""
    gateway = build_demo_gateway(lambda: 2026)
    order = await gateway.orders.get_by_code(DELIVERED)
    await gateway.orders.save(order.model_copy(update={"rating": None}))
    return gateway


def service(principal=CLIENT_3, gateway=None):
    return PortalService(gateway or build_demo_gateway(lambda: 2026), principal, clock=lambda: AT)


# ----------------------------------------------------------------------
# Domínio
# ----------------------------------------------------------------------
def test_score_and_comment_validation():
    assert rating.parse_score(" 10 ") == 10 and rating.parse_score(0) == 0
    for bad in ("11", "-1", "7.5", "", None, "dez"):
        with pytest.raises(ValidationError, match="de 0 a 10"):
            rating.parse_score(bad)
    assert rating.clean_comment("  muito   bom \n ") == "muito bom"
    with pytest.raises(ValidationError, match="500"):
        rating.clean_comment("x" * 501)


def test_classification():
    assert [rating.classify(s) for s in (10, 9, 8, 7, 6, 0)] == [
        "Promotor", "Promotor", "Neutro", "Neutro", "Detrator", "Detrator"]


def test_nps_matches_the_spec_example():
    summary = rating.nps_summary([10, 9, 8, 6, 3])
    assert (summary.promoters, summary.neutrals, summary.detractors) == (2, 1, 2)
    assert summary.nps == 0 and summary.average == 7.2
    assert rating.nps_summary([10, 10, 9, 5]).nps == 50
    assert rating.nps_summary([1, 2, 9]).nps == -33
    empty = rating.nps_summary([])
    assert empty.nps is None and empty.average is None and empty.count == 0


# ----------------------------------------------------------------------
# Serviço do portal
# ----------------------------------------------------------------------
async def test_client_rates_own_delivered_order_once():
    gateway = await unrated_delivered_gateway()
    item = await service(gateway=gateway).rate(DELIVERED, "9", "  Rápido e caprichado ")
    assert item.order.rating == Rating(score=9, comment="Rápido e caprichado", at=AT)
    with pytest.raises(ValidationError, match="já foi avaliada"):
        await service(gateway=gateway).rate(DELIVERED, "10")


async def test_only_delivered_orders_can_be_rated():
    with pytest.raises(ValidationError, match="Só ordens entregues"):
        await service(CLIENT_1).rate(REPAIR, "8")


async def test_other_clients_order_is_not_found():
    gateway = await unrated_delivered_gateway()
    with pytest.raises(NotFoundError):
        await service(CLIENT_1, gateway).rate(DELIVERED, "0")


async def test_only_clients_can_rate():
    assert not has_permission(Principal("1", "Ana", "a@x.test", Role.ADMIN), Permission.PORTAL_RATE)
    with pytest.raises(PermissionDeniedError):
        await service(Principal("1", "Ana", "a@x.test", Role.ADMIN)).rate(DELIVERED, "10")


# ----------------------------------------------------------------------
# Relatórios
# ----------------------------------------------------------------------
async def test_report_counts_ratings_made_in_the_period():
    gateway = build_demo_gateway(lambda: 2026)
    orders, technicians = await gateway.orders.list(), await gateway.technicians.list()
    rated = next(o for o in orders if o.rating)
    day = rated.rating.at.astimezone(BRT).date()
    report = build_report(orders, technicians, Period(day, day))
    s = report.satisfaction
    assert (s.summary.count, s.summary.nps, s.summary.average) == (1, 100, 9.0)
    assert [c.code for c in s.comments] == [rated.code]
    tech = next(t for t in technicians if t.id == rated.technician_id)
    later = build_report(orders, technicians, Period(date(2027, 1, 1), date(2027, 1, 31)))
    assert later.satisfaction.summary.nps is None
    # A média por técnico considera as avaliações feitas no período.
    full = build_report(orders, technicians, Period(date(2026, 1, 1), date(2026, 12, 31)))
    assert next(r for r in full.technicians if r.name == tech.name).average_rating == 9.0


# ----------------------------------------------------------------------
# Xano
# ----------------------------------------------------------------------
CREATED = int(datetime(2026, 11, 1, 9, 0, tzinfo=BRT).timestamp() * 1000)
RATED = int(datetime(2026, 11, 8, 10, 0, tzinfo=BRT).timestamp() * 1000)
XANO_ORDER = {
    "id": 12, "created_at": CREATED, "atualizado_em": CREATED, "cliente_id": 7, "item_cliente_id": 5, "user_id": 2,
    "descricao_problema": "Não liga", "diagnostico": "Fonte", "motivo_cancelamento": None, "status": "entregue",
    "_itens": [], "_pagamentos": [], "_historico": [], "_avaliacao": None,
    "_aparelho": {"id": 5, "cliente_id": 7, "aparelho": "Notebook", "marca": "Dell", "modelo": "Inspiron"},
}


def test_xano_rating_mapping():
    assert mappers.order_from(XANO_ORDER).rating is None
    record = {**XANO_ORDER, "_avaliacao": {"id": 3, "created_at": RATED, "nota": 6, "comentario": "Demorou"}}
    assert mappers.order_from(record).rating == Rating(
        score=6, comment="Demorou", at=datetime(2026, 11, 8, 10, 0, tzinfo=BRT))


async def test_xano_rating_calls_the_portal_endpoint():
    state = {"order": XANO_ORDER}
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.split("/api:", 1)[1].split("/", 1)[1]
        body = json.loads(request.content) if request.content else None
        calls.append((request.method, path, body))
        if path == "portal/minhas_ordens":
            return httpx.Response(200, json=[state["order"]])
        if path == "portal/avaliacao":
            rated = {"id": 3, "created_at": RATED, "os_servicos_id": 12, "cliente_id": 7, "nota": 10,
                     "comentario": "Ótimo"}
            state["order"] = {**XANO_ORDER, "_avaliacao": rated}
            return httpx.Response(200, json=rated)
        return httpx.Response(404, json={"message": ""})

    client = XanoClient("https://exemplo.invalid", 5, transport=httpx.MockTransport(handler),
                        pacer=RequestPacer(10_000, 1), cache=ResponseCache(0))
    gateway = build_xano_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"), client=client)
    use_backend_token("jwt-cliente")
    try:
        principal = Principal("3", "Maria", "m@x.test", Role.CLIENT, client_id="7")
        item = await PortalService(gateway, principal, clock=lambda: AT).rate("OS-2026-00012", "10", "Ótimo")
    finally:
        use_backend_token(None)
    assert item.order.status == OrderStatus.DELIVERED and item.order.rating.score == 10
    assert ("POST", "portal/avaliacao", {"os_servicos_id": 12, "nota": 10, "comentario": "Ótimo"}) in calls
