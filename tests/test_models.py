import pytest

from assistencia_tech.data import errors
from assistencia_tech.models import (
    PHONE_NOT_INFORMED,
    ClientCreate,
    EquipmentCreate,
    OrderCreate,
    ServiceOrder,
    parse_model,
)


def test_client_is_normalized():
    client = parse_model(ClientCreate, {"name": "  Ana  ", "email": " ANA@Exemplo.test ", "phone": ""})
    assert client.name == "Ana"
    assert client.email == "ana@exemplo.test"
    assert client.phone == PHONE_NOT_INFORMED


def test_missing_required_field_names_the_field():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(ClientCreate, {"name": "   ", "email": "ana@exemplo.test"})
    assert info.value.user_message == "Preencha o campo obrigatório: Nome."


def test_absent_field_is_reported_as_required():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(EquipmentCreate, {"client": "Ana", "kind": "Notebook"})
    assert "Marca/modelo" in info.value.user_message


def test_invalid_email_message():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(ClientCreate, {"name": "Ana", "email": "sem-arroba"})
    assert info.value.user_message == "E-mail: informe um e-mail válido."


def test_multiple_errors_are_combined():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(OrderCreate, {"client": "", "device": "", "problem": "Tela"})
    message = info.value.user_message
    assert "Cliente" in message and "Equipamento" in message


def test_service_order_rejects_unknown_status():
    with pytest.raises(errors.ValidationError):
        parse_model(
            ServiceOrder,
            {"code": "OS-2026-00001", "client": "Ana", "device": "X", "problem": "Y", "status": "Perdido"},
        )


def test_user_messages_do_not_leak_technical_details():
    for cls in (
        errors.ConfigurationError,
        errors.ValidationError,
        errors.UnauthorizedError,
        errors.NotFoundError,
        errors.ServiceUnavailableError,
        errors.ContractPendingError,
        errors.UnexpectedError,
    ):
        err = cls(detail="GET https://segredo.invalid/api -> 500 token=abc")
        assert err.user_message == cls.default_message
        for leaked in ("http", "token", "500", "Traceback"):
            assert leaked not in err.user_message
