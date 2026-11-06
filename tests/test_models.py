from decimal import Decimal

import pytest

from assistencia_tech.data import errors
from assistencia_tech.models import (
    ClientCreate,
    EquipmentCreate,
    ItemKind,
    OrderCreate,
    OrderItemCreate,
    PaymentCreate,
    parse_model,
)

VALID_CLIENT = {"name": "Ana", "cpf": "529.982.247-25", "email": "ANA@Exemplo.test", "phone": "(11) 98765-4321"}


def test_client_is_normalized():
    client = parse_model(ClientCreate, {**VALID_CLIENT, "name": "  Ana  "})
    assert client.name == "Ana"
    assert client.cpf == "52998224725"
    assert client.email == "ana@exemplo.test"
    assert client.phone == "11987654321"


def test_missing_cpf_is_required():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(ClientCreate, {**VALID_CLIENT, "cpf": ""})
    assert info.value.user_message == "Preencha o campo obrigatório: CPF."


def test_invalid_cpf_message():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(ClientCreate, {**VALID_CLIENT, "cpf": "123.456.789-00"})
    assert info.value.user_message == "CPF: informe um CPF válido."


def test_invalid_phone_and_email_are_combined():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(ClientCreate, {**VALID_CLIENT, "phone": "98765-432", "email": "sem-arroba"})
    message = info.value.user_message
    assert "Telefone: informe um telefone válido com DDD." in message
    assert "E-mail: informe um e-mail válido." in message


def test_absent_field_is_reported_as_required():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(EquipmentCreate, {"client_id": "1", "kind": "Notebook", "brand": "Dell"})
    assert "Modelo" in info.value.user_message


def test_equipment_kind_must_be_known():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(EquipmentCreate, {"client_id": "1", "kind": "Geladeira", "brand": "X", "model": "Y"})
    assert "Tipo: tipo inválido" in info.value.user_message


def test_equipment_serial_is_uppercased_and_description():
    eq = parse_model(
        EquipmentCreate, {"client_id": "1", "kind": "Tablet", "brand": "Apple", "model": "iPad 9", "serial_number": "abc1"}
    )
    assert eq.serial_number == "ABC1"
    assert eq.description == "Tablet Apple iPad 9"


def test_order_requires_fields():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(OrderCreate, {"client_id": "", "equipment_id": "", "problem": "Tela"})
    assert "Cliente" in info.value.user_message and "Equipamento" in info.value.user_message


def test_item_accepts_brazilian_money_and_quantity_text():
    item = parse_model(
        OrderItemCreate, {"kind": "Peça", "description": "SSD 480 GB", "quantity": "2", "unit_price": "1.250,00"}
    )
    assert item.kind == ItemKind.PART
    assert item.quantity == 2
    assert item.unit_price == Decimal("1250.00")


@pytest.mark.parametrize("price", ["0", "-10", "0,00"])
def test_item_value_must_be_positive(price):
    with pytest.raises(errors.ValidationError) as info:
        parse_model(OrderItemCreate, {"kind": "Serviço", "description": "Limpeza", "unit_price": price})
    assert info.value.user_message == "Valor: o valor deve ser positivo."


@pytest.mark.parametrize("quantity", ["0", "-1", "1,5", "abc"])
def test_item_quantity_must_be_positive_integer(quantity):
    with pytest.raises(errors.ValidationError):
        parse_model(
            OrderItemCreate, {"kind": "Peça", "description": "SSD", "quantity": quantity, "unit_price": "10"}
        )


def test_payment_method_must_be_known():
    with pytest.raises(errors.ValidationError) as info:
        parse_model(PaymentCreate, {"amount": "10", "method": "Cheque"})
    assert "Forma de pagamento" in info.value.user_message


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
