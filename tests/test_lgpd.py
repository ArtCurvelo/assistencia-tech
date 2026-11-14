"""Direitos do titular (LGPD) no portal (mudança add-lgpd-portal)."""

import json
from datetime import datetime

import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.demo.users import DEMO_PASSWORDS
from assistencia_tech.data.errors import AuthenticationError, PermissionDeniedError, ValidationError
from assistencia_tech.data.request_context import use_backend_token
from assistencia_tech.data.xano import XanoClient, build_xano_gateway, mappers
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.permissions import Principal, Role
from assistencia_tech.presenters import client_row
from assistencia_tech.services import AuthService, ClientService, PortalService

pytestmark = pytest.mark.anyio

AT = datetime(2026, 11, 9, 10, 0, tzinfo=BRT)
CAMILA = "camila@example.test"  # cliente 3: só a OS-2026-00120, entregue e avaliada
MARINA = "marina@example.test"  # cliente 1: OS-2026-00125 em reparo
ATTENDANT = Principal("2", "Bia", "b@x.test", Role.ATTENDANT)


async def client_service(email):
    gw = build_demo_gateway(lambda: 2026)
    _, principal = await AuthService(gw).login(email, DEMO_PASSWORDS[email])
    return gw, PortalService(gw, principal, clock=lambda: AT)


async def test_export_has_only_own_data_and_no_internal_authors():
    gw, portal = await client_service(CAMILA)
    data = await portal.export_data()
    assert data["cadastro"]["nome"] == "Camila Souza"
    assert [o["codigo"] for o in data["ordens_de_servico"]] == ["OS-2026-00120"]
    assert data["ordens_de_servico"][0]["avaliacao"]["nota"] == 9
    text = json.dumps(data, ensure_ascii=False)
    assert "Usuário demonstração" not in text and "autor" not in text  # sem autores internos


async def test_wrong_password_changes_nothing():
    gw, portal = await client_service(CAMILA)
    with pytest.raises(PermissionDeniedError, match="Senha incorreta"):
        await portal.delete_account("senha-errada-123")
    assert (await gw.clients.get("3")).name == "Camila Souza"


async def test_open_orders_block_the_deletion():
    gw, portal = await client_service(MARINA)
    with pytest.raises(ValidationError, match="ordens em andamento"):
        await portal.delete_account(DEMO_PASSWORDS[MARINA])


async def test_deletion_anonymizes_keeps_orders_and_blocks_login():
    gw, portal = await client_service(CAMILA)
    await portal.delete_account(DEMO_PASSWORDS[CAMILA])
    client = await gw.clients.get("3")
    assert client.anonymized and client.name == "Cliente anonimizado" and client.cpf == client.email == ""
    order = await gw.orders.get_by_code("OS-2026-00120")
    assert order.client_id == "3" and order.rating.score == 9 and order.rating.comment == ""
    with pytest.raises(AuthenticationError):
        await AuthService(gw).login(CAMILA, DEMO_PASSWORDS[CAMILA])
    rows = [client_row(c) for c in await ClientService(gw, ATTENDANT).list()]
    assert next(r for r in rows if r["id"] == "3")["name"] == "Cliente anonimizado"


def test_xano_reads_anonymized_client_without_validation():
    client = mappers.client_from({"id": 7, "Nome": "Cliente anonimizado", "Cpf": "anonimizado-7",
                                  "email": "anonimizado-7@removido.invalid", "telefone_Aparelho": "",
                                  "anonimizado": True})
    assert client.anonymized and client.cpf == "" and client.email == ""


async def test_xano_calls_the_deletion_endpoint():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.split("/api:", 1)[1].split("/", 1)[1]
        calls.append((request.method, path, json.loads(request.content) if request.content else None))
        if path == "portal/minhas_ordens":
            return httpx.Response(200, json=[])
        if path == "portal/excluir_conta":
            return httpx.Response(200, json={"anonimizado": True})
        return httpx.Response(404, json={"message": ""})

    client = XanoClient("https://exemplo.invalid", 5, transport=httpx.MockTransport(handler),
                        pacer=RequestPacer(10_000, 1), cache=ResponseCache(0))
    gateway = build_xano_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"), client=client)
    use_backend_token("jwt-cliente")
    try:
        principal = Principal("3", "Maria", "m@x.test", Role.CLIENT, client_id="7")
        await PortalService(gateway, principal, clock=lambda: AT).delete_account("SenhaDaMaria1")
    finally:
        use_backend_token(None)
    assert ("POST", "portal/excluir_conta", {"senha": "SenhaDaMaria1"}) in calls
