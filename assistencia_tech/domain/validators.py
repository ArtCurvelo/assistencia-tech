"""Validação, normalização e formatação de CPF, telefone e valores em reais.

Funções puras, sem dependência de interface ou fonte de dados. Erros de
validação são ``ValueError`` com mensagem em português, convertidos em
mensagens de formulário por ``models.validation``.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENTS = Decimal("0.01")


def only_digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


# ----------------------------------------------------------------------
# CPF
# ----------------------------------------------------------------------
def _cpf_check_digit(digits: str) -> int:
    weight = len(digits) + 1
    total = sum(int(d) * (weight - i) for i, d in enumerate(digits))
    return (total * 10) % 11 % 10


def is_valid_cpf(value: str | None) -> bool:
    digits = only_digits(value)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    return _cpf_check_digit(digits[:9]) == int(digits[9]) and _cpf_check_digit(digits[:10]) == int(digits[10])


def normalize_cpf(value: str | None) -> str:
    """Retorna os 11 dígitos do CPF ou lança ``ValueError``."""
    if not is_valid_cpf(value):
        raise ValueError("informe um CPF válido")
    return only_digits(value)


def format_cpf(digits: str) -> str:
    d = only_digits(digits)
    if len(d) != 11:
        return digits
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


# ----------------------------------------------------------------------
# Telefone
# ----------------------------------------------------------------------
def is_valid_phone(value: str | None) -> bool:
    digits = only_digits(value)
    if len(digits) not in (10, 11):
        return False
    if "0" in digits[:2]:  # DDDs brasileiros vão de 11 a 99, sem zero
        return False
    if len(digits) == 11:
        return digits[2] == "9"
    return digits[2] in "2345"


def normalize_phone(value: str | None) -> str:
    """Retorna os dígitos do telefone (DDD + número) ou lança ``ValueError``."""
    if not is_valid_phone(value):
        raise ValueError("informe um telefone válido com DDD")
    return only_digits(value)


def format_phone(digits: str) -> str:
    d = only_digits(digits)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return digits


# ----------------------------------------------------------------------
# Dinheiro
# ----------------------------------------------------------------------
def quantize(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def parse_brl(value: str | int | Decimal) -> Decimal:
    """Converte ``1234.56``, ``1.234,56`` ou ``R$ 1.234,56`` em ``Decimal``.

    Valores com mais de duas casas decimais são recusados, evitando
    ambiguidade entre separador de milhar e decimal (ex.: ``1.234``).
    """
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int) and not isinstance(value, bool):
        number = Decimal(value)
    elif isinstance(value, str):
        text = value.replace("R$", "").replace(" ", "").replace(" ", "")
        if "," in text:
            text = text.replace(".", "").replace(",", ".")
        match = re.fullmatch(r"-?\d+(?:\.(\d+))?", text)
        if not match:
            raise ValueError("informe um valor em reais, por exemplo 1.234,56")
        if match.group(1) and len(match.group(1)) > 2:
            raise ValueError("use no máximo duas casas decimais (ex.: 1.234,56)")
        number = Decimal(text)
    else:
        raise ValueError("informe um valor em reais, por exemplo 1.234,56")
    try:
        if not number.is_finite():
            raise ValueError("informe um valor em reais, por exemplo 1.234,56")
        if number.as_tuple().exponent < -2 and number != quantize(number):
            raise ValueError("use no máximo duas casas decimais")
        return quantize(number)
    except InvalidOperation as exc:  # pragma: no cover - proteção adicional
        raise ValueError("informe um valor em reais, por exemplo 1.234,56") from exc


def format_brl(value: Decimal | int) -> str:
    amount = quantize(Decimal(value))
    sign = "-" if amount < 0 else ""
    text = f"{abs(amount):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{sign}R$ {text}"
