"""Solicitação de atendimento pelo cliente no portal (mudança add-client-self-service).

Funções puras: validam a forma de entrega e os dados da coleta por motoboy.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.errors import ValidationError
from ..models.entities import DELIVERY_COURIER, DELIVERY_MODES, DELIVERY_STORE, PICKUP_PERIODS

MAX_ADDRESS = 200


def parse_delivery(form: Mapping[str, Any]) -> tuple[str, str, str]:
    """Retorna (forma de entrega, endereço de coleta, período); os dois últimos só na coleta por motoboy."""
    mode = str(form.get("delivery_mode", "")).strip()
    if mode not in DELIVERY_MODES:
        raise ValidationError(f"Escolha a forma de entrega: {DELIVERY_STORE} ou {DELIVERY_COURIER}.")
    if mode == DELIVERY_STORE:
        return mode, "", ""
    address = " ".join(str(form.get("pickup_address", "")).split())
    if not address:
        raise ValidationError("Informe o endereço de coleta para o motoboy.")
    if len(address) > MAX_ADDRESS:
        raise ValidationError(f"O endereço de coleta deve ter no máximo {MAX_ADDRESS} caracteres.")
    period = str(form.get("pickup_period", "")).strip()
    if period not in PICKUP_PERIODS:
        raise ValidationError(f"Escolha o período da coleta: {', '.join(PICKUP_PERIODS)}.")
    return mode, address, period


def store_info(address: str | None, hours: str | None) -> dict[str, str]:
    """Endereço e horário da loja para o portal; sem configuração, o sistema não inventa endereço."""
    return {
        "address": address or "Endereço a confirmar com a assistência.",
        "hours": hours or "",
        "configured": "1" if address else "",
    }
