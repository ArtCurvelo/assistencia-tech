"""Decisão do orçamento pelo cliente no portal (mudança add-client-budget-approval)."""

import json
from datetime import datetime

import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import NotFoundError, PermissionDeniedError, ValidationError
from assistencia_tech.data.request_context import use_backend_token
from assistencia_tech.data.xano import XanoClient, build_xano_gateway
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache
from assistencia_tech.domain import order_operations as ops
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.history import KIND_CLIENT_DECISION
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.models import OrderStatus
from assistencia_tech.presenters import portal_timeline
from assistencia_tech.services import PortalService

pytestmark = pytest.mark.anyio

AT = datetime(2026, 11, 7, 15, 0, tzinfo=BRT)
AWAITING = "OS-2026-00123"  # cliente 4 no seed da demonstração
CLIENT_4 = Principal("40", "Rafael Lima", "rafael@exemplo.test", Role.CLIENT, client_id="4")
CLIENT_1 = Principal("6", "Marina Oliveira", "marina@example.test", Role.CLIENT, client_id="1")
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)


def service(principal=CLIENT_4, gateway=None):
    return PortalService(gateway or build_demo_gateway(lambda: 2026), principal, clock=lambda: AT)


# ----------------------------------------------------------------------
# Domínio
# ----------------------------------------------------------------------
async def _awaiting_order():
    return await build_demo_gateway(lambda: 2026).orders.get_by_code(AWAITING)


async def test_approval_moves_to_repair_with_decision_event():
    order = ops.client_decision(await _awaiting_order(), True, "", AT, "Rafael Lima (Cliente)")
    assert order.status == OrderStatus.REPAIR
    decision, status = order.history[-2:]
    assert (decision.kind, decision.description, decision.author) == (
        KIND_CLIENT_DECISION, "Orçamento aprovado pelo cliente.", "Rafael Lima (Cliente)")
    assert status.to_status == "Em reparo"


async def test_refusal_cancels_with_reason():
    order = ops.client_decision(await _awaiting_order(), False, "  Muito caro  ", AT, "Rafael Lima (Cliente)")
    assert order.status == OrderStatus.CANCELLED
    assert order.cancel_reason == "Orçamento recusado pelo cliente: Muito caro"
    assert order.history[-2].description == "Orçamento recusado pelo cliente. Motivo: Muito caro"


async def test_refusal_requires_reason():
    with pytest.raises(ValidationError, match="Informe o motivo da recusa"):
        ops.client_decision(await _awaiting_order(), False, "   ", AT, "x")


async def test_decision_only_while_awaiting_approval():
    order = await build_demo_gateway(lambda: 2026).orders.get_by_code("OS-2026-00125")  # Em reparo
    with pytest.raises(ValidationError, match="não está aguardando a sua aprovação"):
        ops.client_decision(order, True, "", AT, "x")


async def test_portal_timeline_shows_the_decision():
    order = ops.client_decision(await _awaiting_order(), True, "", AT, "Rafael Lima (Cliente)")
    descriptions = [row["description"] for row in portal_timeline(order)]
    assert "Orçamento aprovado pelo cliente." in descriptions
    assert all("Rafael" not in d for d in descriptions)  # o andamento do portal não mostra autores


# ----------------------------------------------------------------------
# Serviço sobre o modo demonstração
# ----------------------------------------------------------------------
async def test_client_approves_own_order():
    gateway = build_demo_gateway(lambda: 2026)
    item = await service(gateway=gateway).decide_budget(AWAITING, True)
    assert item.order.status == OrderStatus.REPAIR
    stored = await gateway.orders.get_by_code(AWAITING)
    assert stored.status == OrderStatus.REPAIR
    assert stored.history[-2].author == "Rafael Lima (Cliente)"


async def test_client_refuses_own_order():
    gateway = build_demo_gateway(lambda: 2026)
    await service(gateway=gateway).decide_budget(AWAITING, False, "Vou comprar outro")
    stored = await gateway.orders.get_by_code(AWAITING)
    assert stored.status == OrderStatus.CANCELLED
    assert "Vou comprar outro" in stored.cancel_reason


async def test_other_clients_order_is_not_found_and_unchanged():
    gateway = build_demo_gateway(lambda: 2026)
    with pytest.raises(NotFoundError):
        await service(CLIENT_1, gateway).decide_budget(AWAITING, True)
    assert (await gateway.orders.get_by_code(AWAITING)).status == OrderStatus.AWAITING_APPROVAL


async def test_staff_cannot_use_the_client_decision():
    with pytest.raises(PermissionDeniedError):
        await service(ATTENDANT).decide_budget(AWAITING, True)


async def test_refusal_without_reason_changes_nothing():
    gateway = build_demo_gateway(lambda: 2026)
    with pytest.raises(ValidationError):
        await service(gateway=gateway).decide_budget(AWAITING, False, "")
    assert (await gateway.orders.get_by_code(AWAITING)).status == OrderStatus.AWAITING_APPROVAL


# ----------------------------------------------------------------------
# Adaptador Xano (servidor simulado)
# ----------------------------------------------------------------------
CREATED = int(datetime(2026, 11, 7, 10, 0, tzinfo=BRT).timestamp() * 1000)
XANO_ORDER = {
    "id": 12, "created_at": CREATED, "atualizado_em": CREATED, "cliente_id": 7, "item_cliente_id": 5, "user_id": 2,
    "descricao_problema": "Não liga", "diagnostico": "Fonte", "motivo_cancelamento": None,
    "status": "aguardando_aprovacao",
    "_itens": [{"id": 40, "tipo": "peca", "descricao": "Fonte", "quantidade": 1, "valor_unitario": 180}],
    "_pagamentos": [], "_historico": [],
    "_aparelho": {"id": 5, "cliente_id": 7, "aparelho": "Notebook", "marca": "Dell", "modelo": "Inspiron"},
}


async def test_xano_decision_calls_the_portal_endpoint():
    state = {"order": XANO_ORDER}
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.split("/api:", 1)[1].split("/", 1)[1]
        body = json.loads(request.content) if request.content else None
        calls.append((request.method, path, body))
        if path == "portal/minhas_ordens":
            return httpx.Response(200, json=[state["order"]])
        if path == "portal/decisao_orcamento":
            state["order"] = {**XANO_ORDER, "status": "em_reparo"}
            return httpx.Response(200, json=state["order"])
        return httpx.Response(404, json={"message": ""})

    client = XanoClient("https://exemplo.invalid", 5, transport=httpx.MockTransport(handler),
                        pacer=RequestPacer(10_000, 1), cache=ResponseCache(0))
    gateway = build_xano_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"), client=client)
    use_backend_token("jwt-cliente")
    try:
        principal = Principal("3", "Maria", "m@x.test", Role.CLIENT, client_id="7")
        item = await PortalService(gateway, principal, clock=lambda: AT).decide_budget("OS-2026-00012", True)
    finally:
        use_backend_token(None)
    assert item.order.status == OrderStatus.REPAIR
    assert ("POST", "portal/decisao_orcamento", {"os_servicos_id": 12, "aprovar": True, "motivo": ""}) in calls
    assert not any(c[1].startswith("os_servicos") or c[1] == "os_historico" for c in calls)
