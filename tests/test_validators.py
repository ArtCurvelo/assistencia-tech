from decimal import Decimal

import pytest

from assistencia_tech.domain.validators import (
    format_brl,
    format_cpf,
    format_phone,
    is_valid_cpf,
    normalize_cpf,
    normalize_phone,
    parse_brl,
)


@pytest.mark.parametrize("cpf", ["529.982.247-25", "52998224725", " 529 982 247 25 ", "123.456.789-09"])
def test_valid_cpfs(cpf):
    assert is_valid_cpf(cpf)


@pytest.mark.parametrize("cpf", ["123.456.789-00", "11111111111", "000.000.000-00", "5299822472", "", None, "abc"])
def test_invalid_cpfs(cpf):
    assert not is_valid_cpf(cpf)


def test_cpf_normalization_and_format():
    assert normalize_cpf("529.982.247-25") == "52998224725"
    assert format_cpf("52998224725") == "529.982.247-25"
    with pytest.raises(ValueError, match="CPF"):
        normalize_cpf("123.456.789-00")


@pytest.mark.parametrize(
    ("raw", "formatted"),
    [
        ("11987654321", "(11) 98765-4321"),
        ("(21) 99876-5432", "(21) 99876-5432"),
        ("1133334444", "(11) 3333-4444"),
        ("(31) 2555-1234", "(31) 2555-1234"),
    ],
)
def test_valid_phones(raw, formatted):
    assert format_phone(normalize_phone(raw)) == formatted


@pytest.mark.parametrize("raw", ["98765-432", "01987654321", "10987654321", "11887654321", "1193334444", ""])
def test_invalid_phones(raw):
    with pytest.raises(ValueError, match="telefone"):
        normalize_phone(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.234,56", Decimal("1234.56")),
        ("1234.56", Decimal("1234.56")),
        ("R$ 1.234,56", Decimal("1234.56")),
        ("45,5", Decimal("45.50")),
        ("120", Decimal("120.00")),
        (Decimal("10.5"), Decimal("10.50")),
        (7, Decimal("7.00")),
    ],
)
def test_parse_brl(raw, expected):
    assert parse_brl(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "1,2,3", "12.345", "1,999", "1.000", "", "R$"])
def test_parse_brl_rejects_invalid_or_ambiguous(raw):
    with pytest.raises(ValueError):
        parse_brl(raw)


def test_parse_brl_accepts_trailing_zeros_beyond_cents():
    assert parse_brl(Decimal("10.500")) == Decimal("10.50")


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (Decimal("1234.56"), "R$ 1.234,56"),
        (Decimal("0"), "R$ 0,00"),
        (Decimal("211"), "R$ 211,00"),
        (Decimal("1000000.5"), "R$ 1.000.000,50"),
        (Decimal("-5"), "-R$ 5,00"),
    ],
)
def test_format_brl(value, text):
    assert format_brl(value) == text
