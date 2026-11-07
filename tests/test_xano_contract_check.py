"""Verificador do contrato-alvo do Xano (sem rede: specs sintéticas e cópias salvas)."""

from tools.xano_contract_check import check_endpoint, load_specs, report
from tools.xano_target_contract import DEFAULT_INSTANCE, ORDER_STATUS_VALUES, TARGET, Endpoint


def _obj(*names, enums=None):
    enums = enums or {}
    return {"type": "object", "properties": {n: ({"type": "string", "enum": list(enums[n])} if n in enums
                                                 else {"type": "string"}) for n in names}}


def _spec(path, method, op):
    return {"paths": {path: {method: op}}}


def _op(request=(), response=(), secured=True, enums=None, array=False):
    schema = _obj(*response, enums=enums)
    if array:
        schema = {"type": "array", "items": schema}
    op = {"responses": {"200": {"content": {"application/json": {"schema": schema}}}}}
    if request:
        op["requestBody"] = {"content": {"application/json": {"schema": _obj(*request)}}}
    if secured:
        op["security"] = [{"bearerAuth": []}]
    return op


TARGET_PATCH = Endpoint("patch", "/os_servicos/{os_servicos_id}", "bearer", ("status", "diagnostico"),
                        ("id", "status", "diagnostico"), {"status": ORDER_STATUS_VALUES})


def test_compliant_endpoint_has_no_problems():
    op = _op(("status", "diagnostico"), ("id", "status", "diagnostico"), enums={"status": ORDER_STATUS_VALUES})
    assert check_endpoint(_spec(TARGET_PATCH.path, "patch", op), TARGET_PATCH) == []


def test_detects_missing_auth_fields_and_wrong_enum():
    op = _op(("status",), ("id", "status"), secured=False, enums={"status": ("aberta", "concluida")})
    problems = check_endpoint(_spec(TARGET_PATCH.path, "patch", op), TARGET_PATCH)
    assert "não exige autenticação (bearerAuth)" in problems
    assert "entrada sem: diagnostico" in problems
    assert "resposta sem: diagnostico" in problems
    assert any(p.startswith("status deve aceitar recebido") for p in problems)


def test_detects_missing_endpoint_undocumented_response_and_group():
    assert check_endpoint({"paths": {}}, TARGET_PATCH) == ["endpoint não existe"]
    op = {"responses": {"200": {"content": {"application/json": {"schema": {"type": "object", "properties": {}}}}}},
          "security": [{"bearerAuth": []}], "requestBody": {"content": {"application/json": {"schema":
          _obj("status", "diagnostico")}}}}
    assert "resposta sem esquema documentado" in check_endpoint(_spec(TARGET_PATCH.path, "patch", op), TARGET_PATCH)
    assert check_endpoint(None, TARGET_PATCH) == ["documentação do grupo indisponível"]


def test_public_endpoint_must_not_require_auth_and_lists_use_item_fields():
    target = Endpoint("get", "/consulta_publica/{id}", "public", (), ("id", "status"))
    ok = _op(response=("id", "status"), secured=False, array=True)
    assert check_endpoint(_spec(target.path, "get", ok), target) == []
    secured = _op(response=("id", "status"), secured=True)
    assert check_endpoint(_spec(target.path, "get", secured), target) == ["deveria ser público"]


def test_query_parameters_count_as_request_fields():
    target = Endpoint("get", "/cliente", "bearer", ("busca", "page"), ("items",))
    op = _op(response=("items",))
    op["parameters"] = [{"name": "busca", "in": "query"}, {"name": "page", "in": "query"}]
    assert check_endpoint(_spec("/cliente", "get", op), target) == []


COLLEAGUE_GROUP_IDS = {"auth": "GRUPO-AUTH-COLEGA", "cliente": "GRUPO-CLIENTE-COLEGA", "os": "GRUPO-OS-COLEGA"}


def test_saved_snapshots_report_current_gaps():
    # Cópias da documentação do workspace original do grupo (antes do backend próprio).
    text, pending = report(load_specs(True, DEFAULT_INSTANCE, COLLEAGUE_GROUP_IDS), COLLEAGUE_GROUP_IDS)
    total = sum(len(e) for e in TARGET.values())
    assert pending == total - 1  # somente POST /auth/login já atende ao alvo
    assert "[OK ] POST   /auth/login" in text
    assert "role deve aceitar admin, atendente, tecnico, cliente (hoje: admin, member)" in text


def test_custom_instance_and_group_ids(monkeypatch):
    calls = []

    class FakeResponse:
        status_code = 404

        def json(self):
            return {}

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse()

    monkeypatch.setattr("tools.xano_contract_check.httpx.get", fake_get)
    specs = load_specs(False, "https://exemplo.invalid/", {"auth": "AAAA", "cliente": "BBBB", "os": "CCCC"})
    assert calls == ["https://exemplo.invalid/apispec:AAAA", "https://exemplo.invalid/apispec:BBBB",
                     "https://exemplo.invalid/apispec:CCCC"]
    assert set(specs.values()) == {None}
    text, _ = report(specs, {"auth": "AAAA", "cliente": "BBBB", "os": "CCCC"})
    assert "(api:AAAA)" in text and "documentação do grupo indisponível" in text


def test_own_backend_snapshots_meet_the_whole_target():
    # Cópias da documentação do backend em XanoScript (workspace 170741), grupos padrão.
    text, pending = report(load_specs(offline=True))
    assert pending == 0, text
