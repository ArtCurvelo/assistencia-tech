"""Modelos de domínio do Assistência TECH."""

from .entities import (
    EQUIPMENT_KINDS,
    ORDER_STATUSES,
    PHONE_NOT_INFORMED,
    Client,
    ClientCreate,
    Equipment,
    EquipmentCreate,
    OrderCreate,
    ServiceOrder,
)
from .validation import parse_model

__all__ = [
    "EQUIPMENT_KINDS",
    "ORDER_STATUSES",
    "PHONE_NOT_INFORMED",
    "Client",
    "ClientCreate",
    "Equipment",
    "EquipmentCreate",
    "OrderCreate",
    "ServiceOrder",
    "parse_model",
]
