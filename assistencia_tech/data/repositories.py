"""Interfaces internas de acesso a dados.

O estado Reflex depende apenas destas interfaces. Cada fonte de dados
(demonstração, Xano) fornece uma implementação compatível.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..models import Client, ClientCreate, Equipment, EquipmentCreate, OrderCreate, ServiceOrder


@runtime_checkable
class ClientRepository(Protocol):
    async def list(self) -> list[Client]: ...

    async def create(self, data: ClientCreate) -> Client: ...


@runtime_checkable
class EquipmentRepository(Protocol):
    async def list(self) -> list[Equipment]: ...

    async def create(self, data: EquipmentCreate) -> Equipment: ...


@runtime_checkable
class OrderRepository(Protocol):
    async def list(self) -> list[ServiceOrder]: ...

    async def get_by_code(self, code: str) -> ServiceOrder:
        """Retorna a ordem ou lança ``NotFoundError``."""
        ...

    async def create(self, data: OrderCreate) -> ServiceOrder: ...

    async def update_status(self, code: str, status: str) -> ServiceOrder:
        """Lança ``ValidationError`` (status inválido) ou ``NotFoundError``."""
        ...


@dataclass(frozen=True)
class DataGateway:
    """Agrupa os repositórios de uma fonte de dados."""

    source: str
    label: str
    is_demo: bool
    clients: ClientRepository
    equipment: EquipmentRepository
    orders: OrderRepository
