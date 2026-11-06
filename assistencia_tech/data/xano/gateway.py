"""Adaptador Xano das interfaces de repositório.

Cada operação exige um contrato registrado. Como o mapeamento entre as
respostas do Xano e os modelos internos depende da documentação oficial
(tarefa 6.2), operações com contrato registrado mas sem mapeamento também
falham de forma explícita, sem enviar requisições.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...config import DATA_SOURCE_XANO, Settings
from ...models import Client, ClientCreate, Equipment, EquipmentCreate, OrderCreate, ServiceOrder
from ..errors import ContractPendingError
from ..repositories import DataGateway
from .client import XanoClient
from .contracts import EndpointContract, require_contract


class _XanoRepository:
    def __init__(self, client: XanoClient, registry: Mapping[str, EndpointContract] | None) -> None:
        self._client = client
        self._registry = registry

    def _pending(self, operation: str) -> ContractPendingError:
        require_contract(operation, self._registry)
        return ContractPendingError(
            "A integração com o Xano para esta operação ainda está em implementação.",
            detail=f"contrato de '{operation}' registrado, mas sem mapeamento de resposta",
        )


class XanoClientRepository(_XanoRepository):
    async def list(self) -> list[Client]:
        raise self._pending("clients.list")

    async def create(self, data: ClientCreate) -> Client:
        raise self._pending("clients.create")


class XanoEquipmentRepository(_XanoRepository):
    async def list(self) -> list[Equipment]:
        raise self._pending("equipment.list")

    async def create(self, data: EquipmentCreate) -> Equipment:
        raise self._pending("equipment.create")


class XanoOrderRepository(_XanoRepository):
    async def list(self) -> list[ServiceOrder]:
        raise self._pending("orders.list")

    async def get_by_code(self, code: str) -> ServiceOrder:
        raise self._pending("orders.get_by_code")

    async def create(self, data: OrderCreate) -> ServiceOrder:
        raise self._pending("orders.create")

    async def update_status(self, code: str, status: str) -> ServiceOrder:
        raise self._pending("orders.update_status")


def build_xano_gateway(
    settings: Settings,
    *,
    client: XanoClient | None = None,
    registry: Mapping[str, EndpointContract] | None = None,
) -> DataGateway:
    client = client or XanoClient(settings.xano_base_url, settings.xano_timeout_seconds)
    return DataGateway(
        source=DATA_SOURCE_XANO,
        label="Backend Xano",
        is_demo=False,
        clients=XanoClientRepository(client, registry),
        equipment=XanoEquipmentRepository(client, registry),
        orders=XanoOrderRepository(client, registry),
    )
