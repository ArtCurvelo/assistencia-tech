"""Modo demonstração: repositórios em memória.

Os dados existem apenas enquanto o processo da aplicação estiver em execução
e são sempre identificados como demonstrativos na interface. Regras de
negócio não ficam aqui: estão em ``domain`` e ``services``.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date

from ...config import DATA_SOURCE_DEMO
from ...models import Client, ClientCreate, Equipment, EquipmentCreate, ServiceOrder, Technician
from ..errors import NotFoundError, ValidationError
from ..repositories import DataGateway
from . import seed
from .auth import DemoAuthProvider
from .users import seed_users

YearProvider = Callable[[], int]
_CODE_RE = re.compile(r"^OS-(\d{4})-(\d+)$")


def format_order_code(year: int, number: int) -> str:
    return f"OS-{year}-{number:05d}"


def next_order_code(existing_codes: list[str], year: int) -> str:
    """Próximo código sequencial do ano, no formato ``OS-AAAA-NNNNN``."""
    numbers = [
        int(match.group(2))
        for code in existing_codes
        if (match := _CODE_RE.match(code.strip().upper())) and int(match.group(1)) == year
    ]
    return format_order_code(year, max(numbers, default=0) + 1)


def _next_id(ids: list[str]) -> str:
    return str(max((int(i) for i in ids if i.isdigit()), default=0) + 1)


class _MemoryRepository:
    entity_label = "Registro"

    def __init__(self, items: list) -> None:
        self.items = list(items)

    async def list(self) -> list:
        return list(self.items)

    async def get(self, item_id: str):
        for item in self.items:
            if item.id == item_id:
                return item
        raise NotFoundError(f"{self.entity_label} não encontrado.")

    async def update(self, entity):
        await self.get(entity.id)
        self.items = [entity if item.id == entity.id else item for item in self.items]
        return entity

    async def delete(self, item_id: str) -> None:
        await self.get(item_id)
        self.items = [item for item in self.items if item.id != item_id]


class DemoClientRepository(_MemoryRepository):
    entity_label = "Cliente"

    async def create(self, data: ClientCreate) -> Client:
        client = Client(id=_next_id([c.id for c in self.items]), **data.model_dump())
        self.items.append(client)
        return client


class DemoEquipmentRepository(_MemoryRepository):
    entity_label = "Equipamento"

    async def create(self, data: EquipmentCreate) -> Equipment:
        equipment = Equipment(id=_next_id([e.id for e in self.items]), **data.model_dump())
        self.items.append(equipment)
        return equipment


class DemoTechnicianRepository:
    def __init__(self, items: list[Technician]) -> None:
        self.items = list(items)

    async def list(self) -> list[Technician]:
        return list(self.items)


class DemoOrderRepository:
    def __init__(self, items: list[ServiceOrder], year_provider: YearProvider) -> None:
        self.items = list(items)
        self._year = year_provider

    async def list(self) -> list[ServiceOrder]:
        return sorted(self.items, key=lambda o: (o.opened_at, o.code), reverse=True)

    def _index_of(self, code: str) -> int:
        wanted = code.strip().upper()
        for index, order in enumerate(self.items):
            if order.code.upper() == wanted:
                return index
        raise NotFoundError(f"Ordem de serviço não encontrada: {code.strip() or '(vazio)'}.")

    async def get_by_code(self, code: str) -> ServiceOrder:
        return self.items[self._index_of(code)]

    async def next_code(self) -> str:
        return next_order_code([o.code for o in self.items], self._year())

    async def create(self, order: ServiceOrder) -> ServiceOrder:
        if any(o.code.upper() == order.code.upper() for o in self.items):
            raise ValidationError(f"Já existe uma ordem com o código {order.code}.")
        self.items.append(order)
        return order

    async def save(self, order: ServiceOrder) -> ServiceOrder:
        self.items[self._index_of(order.code)] = order
        return order


def build_demo_gateway(year_provider: YearProvider | None = None) -> DataGateway:
    """Cria um gateway de demonstração com os dados fictícios iniciais."""
    return DataGateway(
        source=DATA_SOURCE_DEMO,
        label="Modo demonstração",
        is_demo=True,
        clients=DemoClientRepository(seed.seed_clients()),
        equipment=DemoEquipmentRepository(seed.seed_equipment()),
        technicians=DemoTechnicianRepository(seed.seed_technicians()),
        orders=DemoOrderRepository(seed.seed_orders(), year_provider or (lambda: date.today().year)),
        auth=DemoAuthProvider(seed_users()),
    )
