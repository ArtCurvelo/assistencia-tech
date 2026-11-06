import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data import errors
from assistencia_tech.data.xano import (
    CONTRACTS,
    OPERATIONS,
    EndpointContract,
    XanoClient,
    build_xano_gateway,
    require_contract,
)
from datetime import datetime

from assistencia_tech.domain.clock import BRT
from assistencia_tech.models import Client, ClientCreate, Equipment, EquipmentCreate, ServiceOrder

CLIENT_DATA = ClientCreate(name="Ana", cpf="52998224725", email="ana@exemplo.test", phone="11987654321")
EQUIPMENT_DATA = EquipmentCreate(client_id="1", kind="Notebook", brand="Dell", model="Inspiron")
_AT = datetime(2026, 11, 6, tzinfo=BRT)
ORDER = ServiceOrder(code="OS-2026-00001", client_id="1", equipment_id="1", problem="X", opened_at=_AT, updated_at=_AT)

pytestmark = pytest.mark.anyio

BASE_URL = "https://exemplo.invalid/api"


def make_client(handler, timeout=5.0) -> XanoClient:
    return XanoClient(BASE_URL, timeout, transport=httpx.MockTransport(handler))


def test_client_requires_base_url():
    with pytest.raises(errors.ConfigurationError) as info:
        XanoClient(None, 10)
    assert "XANO_BASE_URL" in info.value.user_message


async def test_successful_json_response_and_request_shape():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["method"] = request.method
        return httpx.Response(200, json={"ok": True})

    result = await make_client(handler).request("GET", "/qualquer", params={"q": "1"})
    assert result == {"ok": True}
    assert seen == {"url": f"{BASE_URL}/qualquer?q=1", "method": "GET"}


async def test_empty_body_returns_none():
    result = await make_client(lambda r: httpx.Response(204)).request("DELETE", "/x")
    assert result is None


async def test_non_json_body_is_unexpected():
    with pytest.raises(errors.UnexpectedError):
        await make_client(lambda r: httpx.Response(200, text="<html>")).request("GET", "/x")


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (400, errors.ValidationError),
        (422, errors.ValidationError),
        (401, errors.UnauthorizedError),
        (403, errors.UnauthorizedError),
        (404, errors.NotFoundError),
        (408, errors.ServiceUnavailableError),
        (429, errors.ServiceUnavailableError),
        (500, errors.ServiceUnavailableError),
        (503, errors.ServiceUnavailableError),
        (418, errors.UnexpectedError),
    ],
)
async def test_status_codes_are_translated(status, expected):
    client = make_client(lambda r: httpx.Response(status, json={"message": "detalhe interno"}))
    with pytest.raises(expected) as info:
        await client.request("GET", "/x")
    assert "detalhe interno" not in info.value.user_message


async def test_timeout_is_service_unavailable():
    def handler(request):
        raise httpx.ReadTimeout("lento", request=request)

    with pytest.raises(errors.ServiceUnavailableError):
        await make_client(handler).request("GET", "/x")


async def test_connection_failure_is_service_unavailable():
    def handler(request):
        raise httpx.ConnectError("sem rede", request=request)

    with pytest.raises(errors.ServiceUnavailableError):
        await make_client(handler).request("GET", "/x")


def test_contract_registry_starts_empty():
    # Nenhum contrato pode existir antes da documentação oficial.
    assert CONTRACTS == {}


def test_require_contract_unknown_operation():
    with pytest.raises(KeyError):
        require_contract("nao.existe")


def test_require_contract_returns_registered_contract():
    contract = EndpointContract(method="GET", path="/exemplo", source="teste")
    assert require_contract("clients.list", {"clients.list": contract}) is contract


async def test_xano_gateway_sends_no_requests_without_contracts():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=[])

    gateway = build_xano_gateway(
        Settings(data_source="xano", xano_base_url=BASE_URL), client=make_client(handler)
    )
    assert gateway.is_demo is False
    client = Client(id="1", **CLIENT_DATA.model_dump())
    operations = {
        "clients.list": gateway.clients.list(),
        "clients.get": gateway.clients.get("1"),
        "clients.create": gateway.clients.create(CLIENT_DATA),
        "clients.update": gateway.clients.update(client),
        "clients.delete": gateway.clients.delete("1"),
        "equipment.list": gateway.equipment.list(),
        "equipment.get": gateway.equipment.get("1"),
        "equipment.create": gateway.equipment.create(EQUIPMENT_DATA),
        "equipment.update": gateway.equipment.update(Equipment(id="1", **EQUIPMENT_DATA.model_dump())),
        "equipment.delete": gateway.equipment.delete("1"),
        "technicians.list": gateway.technicians.list(),
        "orders.list": gateway.orders.list(),
        "orders.get_by_code": gateway.orders.get_by_code("OS-2026-00001"),
        "orders.next_code": gateway.orders.next_code(),
        "orders.create": gateway.orders.create(ORDER),
        "orders.save": gateway.orders.save(ORDER),
    }
    assert set(operations) == set(OPERATIONS)
    for name, operation in operations.items():
        with pytest.raises(errors.ContractPendingError) as info:
            await operation
        assert "documentação oficial" in info.value.user_message, name
    assert calls == []


async def test_registered_contract_without_mapping_still_sends_nothing():
    calls = []
    registry = {"clients.list": EndpointContract(method="GET", path="/exemplo", source="teste")}
    gateway = build_xano_gateway(
        Settings(data_source="xano", xano_base_url=BASE_URL),
        client=make_client(lambda r: calls.append(r) or httpx.Response(200, json=[])),
        registry=registry,
    )
    with pytest.raises(errors.ContractPendingError, match="em implementação"):
        await gateway.clients.list()
    assert calls == []
