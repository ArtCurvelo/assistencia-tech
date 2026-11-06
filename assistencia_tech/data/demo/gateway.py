"""Modo demonstração: repositórios em memória.

Os dados existem apenas enquanto o processo da aplicação estiver em execução
e são sempre identificados como demonstrativos na interface.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date

from ...config import DATA_SOURCE_DEMO
from ...models import (
    ORDER_STATUSES,
    Client,
    ClientCreate,
    Equipment,
    EquipmentCreate,
    OrderCreate,
    ServiceOrder,
)
from ...services import demo_data
from ..errors import NotFoundError, ValidationError
from ..repositories import DataGateway

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


def _next_id(items: list[Client] | list[Equipment]) -> str:
    return str(max((int(item.id) for item in items if item.id.isdigit()), default=0) + 1)


class _ClientNames:
    """Consulta compartilhada para validar o vínculo com clientes cadastrados."""

    def __init__(self, clients: DemoClientRepository) -> None:
        self._clients = clients

    def require(self, name: str) -> None:
        if all(client.name != name for client in self._clients.items):
            raise ValidationError(f"Cliente não encontrado: {name}. Cadastre o cliente antes de continuar.")


class DemoClientRepository:
    def __init__(self, items: list[Client]) -> None:
        self.items = list(items)

    async def list(self) -> list[Client]:
        return list(self.items)

    async def create(self, data: ClientCreate) -> Client:
        if any(client.email == data.email for client in self.items):
            raise ValidationError(f"Já existe um cliente com o e-mail {data.email}.")
        client = Client(id=_next_id(self.items), **data.model_dump())
        self.items.append(client)
        return client


class DemoEquipmentRepository:
    def __init__(self, items: list[Equipment], clients: _ClientNames) -> None:
        self.items = list(items)
        self._clients = clients

    async def list(self) -> list[Equipment]:
        return list(self.items)

    async def create(self, data: EquipmentCreate) -> Equipment:
        self._clients.require(data.client)
        equipment = Equipment(id=_next_id(self.items), **data.model_dump())
        self.items.append(equipment)
        return equipment


class DemoOrderRepository:
    def __init__(self, items: list[ServiceOrder], clients: _ClientNames, year_provider: YearProvider) -> None:
        self.items = list(items)
        self._clients = clients
        self._year = year_provider

    async def list(self) -> list[ServiceOrder]:
        return list(self.items)

    def _index_of(self, code: str) -> int:
        wanted = code.strip().upper()
        for index, order in enumerate(self.items):
            if order.code.upper() == wanted:
                return index
        raise NotFoundError(f"Ordem de serviço não encontrada: {code.strip() or '(vazio)'}.")

    async def get_by_code(self, code: str) -> ServiceOrder:
        return self.items[self._index_of(code)]

    async def create(self, data: OrderCreate) -> ServiceOrder:
        self._clients.require(data.client)
        code = next_order_code([order.code for order in self.items], self._year())
        order = ServiceOrder(code=code, status=ORDER_STATUSES[0], **data.model_dump())
        self.items.insert(0, order)
        return order

    async def update_status(self, code: str, status: str) -> ServiceOrder:
        if status not in ORDER_STATUSES:
            raise ValidationError(f"Status inválido: {status}. Use: {', '.join(ORDER_STATUSES)}.")
        index = self._index_of(code)
        updated = self.items[index].model_copy(update={"status": status})
        self.items[index] = updated
        return updated


def build_demo_gateway(year_provider: YearProvider | None = None) -> DataGateway:
    """Cria um gateway de demonstração com os dados iniciais fictícios."""
    clients = DemoClientRepository([Client(**c) for c in demo_data.initial_clients()])
    names = _ClientNames(clients)
    return DataGateway(
        source=DATA_SOURCE_DEMO,
        label="Modo demonstração",
        is_demo=True,
        clients=clients,
        equipment=DemoEquipmentRepository([Equipment(**e) for e in demo_data.initial_equipment()], names),
        orders=DemoOrderRepository(
            [ServiceOrder(**o) for o in demo_data.initial_orders()],
            names,
            year_provider or (lambda: date.today().year),
        ),
    )
