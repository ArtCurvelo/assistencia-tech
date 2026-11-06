"""Interfaces internas de persistência.

Os repositórios apenas gravam e leem dados; regras de negócio ficam em
``domain`` e a orquestração em ``services``. Cada fonte de dados
(demonstração, Xano) fornece uma implementação compatível.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..models import Client, ClientCreate, Equipment, EquipmentCreate, ServiceOrder, Technician


@runtime_checkable
class ClientRepository(Protocol):
    async def list(self) -> list[Client]: ...

    async def get(self, client_id: str) -> Client:
        """Retorna o cliente ou lança ``NotFoundError``."""
        ...

    async def create(self, data: ClientCreate) -> Client: ...

    async def update(self, client: Client) -> Client: ...

    async def delete(self, client_id: str) -> None: ...


@runtime_checkable
class EquipmentRepository(Protocol):
    async def list(self) -> list[Equipment]: ...

    async def get(self, equipment_id: str) -> Equipment:
        """Retorna o equipamento ou lança ``NotFoundError``."""
        ...

    async def create(self, data: EquipmentCreate) -> Equipment: ...

    async def update(self, equipment: Equipment) -> Equipment: ...

    async def delete(self, equipment_id: str) -> None: ...


@runtime_checkable
class TechnicianRepository(Protocol):
    async def list(self) -> list[Technician]: ...


@runtime_checkable
class OrderRepository(Protocol):
    async def list(self) -> list[ServiceOrder]:
        """Ordens da mais recente para a mais antiga."""
        ...

    async def get_by_code(self, code: str) -> ServiceOrder:
        """Retorna a ordem (código sem distinção de caixa) ou lança ``NotFoundError``."""
        ...

    async def next_code(self) -> str:
        """Próximo código único no formato ``OS-AAAA-NNNNN``."""
        ...

    async def create(self, order: ServiceOrder) -> ServiceOrder: ...

    async def save(self, order: ServiceOrder) -> ServiceOrder:
        """Grava o agregado completo (itens, pagamentos e histórico)."""
        ...


@dataclass(frozen=True)
class DataGateway:
    """Agrupa os repositórios de uma fonte de dados."""

    source: str
    label: str
    is_demo: bool
    clients: ClientRepository
    equipment: EquipmentRepository
    technicians: TechnicianRepository
    orders: OrderRepository
