"""Cliente HTTP do Xano, tradução de erros e registro de contratos."""

import httpx
import pytest

from assistencia_tech.config import Settings, load_settings
from assistencia_tech.data import errors
from assistencia_tech.data.request_context import (
    current_backend_token,
    issue_backend_token,
    take_issued_token,
    use_backend_token,
)
from assistencia_tech.data.xano import CONTRACTS, OPERATIONS, EndpointContract, XanoClient, require_contract
from assistencia_tech.data.xano.client import server_message
from tools.xano_target_contract import TARGET

pytestmark = pytest.mark.anyio

BASE_URL = "https://exemplo.invalid"


@pytest.fixture(autouse=True)
def _token():
    use_backend_token("jwt-de-teste")
    yield
    use_backend_token(None)
    take_issued_token()


def make_client(handler, timeout=5.0) -> XanoClient:
    return XanoClient(BASE_URL, timeout, transport=httpx.MockTransport(handler))


def test_client_requires_base_url():
    with pytest.raises(errors.ConfigurationError) as info:
        XanoClient(None, 10)
    assert "XANO_BASE_URL" in info.value.user_message


def test_settings_have_group_defaults_and_overrides():
    defaults = load_settings({})
    assert (defaults.xano_group_auth, defaults.xano_group_cliente, defaults.xano_group_os) == (
        "assistencia-tech-auth",
        "assistencia-tech-cliente",
        "assistencia-tech-os",
    )
    custom = load_settings({"XANO_GROUP_AUTH": " AAAA ", "XANO_GROUP_OS": "CCCC"})
    assert (custom.xano_group_auth, custom.xano_group_cliente, custom.xano_group_os) == (
        "AAAA",
        "assistencia-tech-cliente",
        "CCCC",
    )


async def test_request_uses_group_url_and_bearer_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"ok": True})

    result = await make_client(handler).request("GET", "grupo-x", "/qualquer", params={"q": "1"})
    assert result == {"ok": True}
    assert seen == {"url": f"{BASE_URL}/api:grupo-x/qualquer?q=1", "auth": "Bearer jwt-de-teste"}


async def test_public_request_sends_no_token():
    seen = {}

    def handler(request):
        seen["auth"] = request.headers.get("Authorization")
        return httpx.Response(200, json={})

    await make_client(handler).request("POST", "g", "/auth/login", json={}, authenticated=False)
    assert seen == {"auth": None}


async def test_authenticated_request_without_token_sends_nothing():
    use_backend_token(None)
    calls = []
    client = make_client(lambda r: calls.append(r) or httpx.Response(200, json={}))
    with pytest.raises(errors.AuthenticationError):
        await client.request("GET", "g", "/x")
    assert calls == []


async def test_empty_body_returns_none():
    result = await make_client(lambda r: httpx.Response(204)).request("DELETE", "g", "/x")
    assert result is None


async def test_non_json_body_is_unexpected():
    with pytest.raises(errors.UnexpectedError):
        await make_client(lambda r: httpx.Response(200, text="<html>")).request("GET", "g", "/x")


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (400, errors.ValidationError),
        (422, errors.ValidationError),
        (401, errors.AuthenticationError),
        (403, errors.PermissionDeniedError),
        (404, errors.NotFoundError),
        (408, errors.ServiceUnavailableError),
        (429, errors.ServiceUnavailableError),
        (500, errors.ServiceUnavailableError),
        (503, errors.ServiceUnavailableError),
        (418, errors.UnexpectedError),
    ],
)
async def test_native_xano_errors_never_reach_the_user(status, expected):
    # Erro nativo do Xano: payload objeto (ou ausente) e mensagem técnica em inglês.
    body = {"code": "ERROR_CODE_INPUT_ERROR", "message": "Missing param: Cpf", "payload": {"param": "Cpf"}}
    client = make_client(lambda r: httpx.Response(status, json=body))
    with pytest.raises(expected) as info:
        await client.request("GET", "g", "/x")
    assert "Missing param" not in info.value.user_message
    assert "Missing param" in (info.value.detail or "")


@pytest.mark.parametrize(
    ("status", "expected"),
    [(400, errors.ValidationError), (403, errors.PermissionDeniedError), (404, errors.NotFoundError)],
)
async def test_precondition_messages_are_shown(status, expected):
    body = {"code": "ERROR_CODE_INPUT_ERROR", "message": "Já existe um cliente com este CPF.", "payload": ""}
    client = make_client(lambda r: httpx.Response(status, json=body))
    with pytest.raises(expected) as info:
        await client.request("POST", "g", "/cliente")
    assert info.value.user_message == "Já existe um cliente com este CPF."


def test_server_message_rule():
    assert server_message({"message": "Informe o CPF.", "payload": ""}) == "Informe o CPF."
    assert server_message({"message": "Unauthorized"}) is None
    assert server_message({"message": "Invalid", "payload": {"param": "x"}}) is None
    assert server_message({"message": "  ", "payload": ""}) is None
    assert server_message(None) is None


async def test_timeout_is_service_unavailable():
    def handler(request):
        raise httpx.ReadTimeout("lento", request=request)

    with pytest.raises(errors.ServiceUnavailableError):
        await make_client(handler).request("GET", "g", "/x")


async def test_connection_failure_is_service_unavailable():
    def handler(request):
        raise httpx.ConnectError("sem rede", request=request)

    with pytest.raises(errors.ServiceUnavailableError):
        await make_client(handler).request("GET", "g", "/x")


def test_issued_token_is_taken_once():
    use_backend_token(None)
    issue_backend_token("novo")
    assert current_backend_token() == "novo"
    assert take_issued_token() == "novo"
    assert take_issued_token() is None


def test_every_operation_has_a_contract_from_the_target():
    # Cada contrato registrado corresponde a um endpoint do contrato-alvo verificado.
    assert set(CONTRACTS) == set(OPERATIONS)
    target = {(e.method.upper(), e.path) for endpoints in TARGET.values() for e in endpoints}
    for name, contract in CONTRACTS.items():
        assert (contract.method, contract.path) in target, name
        assert contract.source.startswith("apispec:"), name


def test_only_login_signup_and_public_lookup_are_public():
    public = {name for name, contract in CONTRACTS.items() if contract.public}
    assert public == {"auth.login", "auth.signup_client", "portal.public_order"}


def test_require_contract_unknown_operation():
    with pytest.raises(KeyError):
        require_contract("nao.existe")


def test_missing_contract_is_pending_and_sends_nothing():
    with pytest.raises(errors.ContractPendingError) as info:
        require_contract("clients.list", {})
    assert "documentação oficial" in info.value.user_message


def test_require_contract_returns_registered_contract():
    contract = EndpointContract(method="GET", group="cliente", path="/exemplo", source="teste")
    assert require_contract("clients.list", {"clients.list": contract}) is contract


def test_settings_type_is_unchanged_for_demo():
    assert Settings().data_source == "demo"


# ----------------------------------------------------------------------
# Limite de requisições do plano e cache de leituras
# ----------------------------------------------------------------------
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache  # noqa: E402


class FakeTime:
    def __init__(self):
        self.now = 0.0
        self.slept = []

    def clock(self):
        return self.now

    async def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


async def test_pacer_waits_when_the_window_is_full():
    fake = FakeTime()
    pacer = RequestPacer(3, 20, clock=fake.clock, sleep=fake.sleep)
    for _ in range(3):
        await pacer.acquire()
    assert fake.slept == []
    await pacer.acquire()
    assert len(fake.slept) == 1 and fake.slept[0] == pytest.approx(20.05)


def test_cache_expires():
    fake = FakeTime()
    cache = ResponseCache(10, clock=fake.clock)
    cache.put(("k",), 1)
    assert cache.get(("k",)) == (True, 1)
    fake.now = 11
    assert cache.get(("k",)) == (False, None)


def paced_client(handler, fake):
    return XanoClient(
        BASE_URL, 5, transport=httpx.MockTransport(handler),
        pacer=RequestPacer(10, 20, clock=fake.clock, sleep=fake.sleep), cache=ResponseCache(15, clock=fake.clock),
    )


async def test_reads_are_cached_per_token_and_writes_clear_the_cache():
    calls = []
    client = paced_client(lambda r: calls.append(r.method) or httpx.Response(200, json={"n": len(calls)}), FakeTime())
    first = await client.request("GET", "g", "/x")
    assert await client.request("GET", "g", "/x") == first
    use_backend_token("outro-usuario")
    await client.request("GET", "g", "/x")
    await client.request("POST", "g", "/y", json={})
    await client.request("GET", "g", "/x")
    assert calls == ["GET", "GET", "POST", "GET"]


async def test_429_waits_for_the_window_and_retries_once():
    fake = FakeTime()
    responses = iter([httpx.Response(429, json={"message": "limit"}), httpx.Response(200, json={"ok": 1})])
    client = paced_client(lambda r: next(responses), fake)
    assert await client.request("GET", "g", "/x") == {"ok": 1}
    assert fake.slept == [20]


async def test_repeated_429_is_service_unavailable():
    fake = FakeTime()
    client = paced_client(lambda r: httpx.Response(429, json={"message": "limit"}), fake)
    with pytest.raises(errors.ServiceUnavailableError):
        await client.request("GET", "g", "/x")
