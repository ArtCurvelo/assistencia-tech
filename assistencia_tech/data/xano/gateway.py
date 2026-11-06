"""Adaptador Xano das interfaces de repositório.

Cada operação exige um contrato registrado. Como o mapeamento entre as
respostas do Xano e os modelos internos depende da documentação oficial
(tarefa 6.2 de ``integrate-xano-backend``), operações com contrato registrado
mas sem mapeamento também falham de forma explícita, sem enviar requisições.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...config import DATA_SOURCE_XANO, Settings
from ...models import Client, ClientCreate, Equipment, EquipmentCreate, ServiceOrder, Technician
from ..errors import ContractPendingError
from ..repositories import DataGateway
from .client import XanoClient
from .contracts import EndpointContract, require_contract


class _XanoRepository:
    prefix = ""

    def __init__(self, client: XanoClient, registry: Mapping[str, EndpointContract] | None) -> None:
        self._client = client
        self._registry = registry

    def _pending(self, action: str) -> ContractPendingError:
        operation = f"{self.prefix}.{action}"
        require_contract(operation, self._registry)
        return ContractPendingError(
            "A integração com o Xano para esta operação ainda está em implementação.",
            detail=f"contrato de '{operation}' registrado, mas sem mapeamento de resposta",
        )


class XanoClientRepository(_XanoRepository):
    prefix = "clients"

    async def list(self) -> list[Client]:
        raise self._pending("list")

    async def get(self, client_id: str) -> Client:
        raise self._pending("get")

    async def create(self, data: ClientCreate) -> Client:
        raise self._pending("create")

    async def update(self, client: Client) -> Client:
        raise self._pending("update")

    async def delete(self, client_id: str) -> None:
        raise self._pending("delete")


class XanoEquipmentRepository(_XanoRepository):
    prefix = "equipment"

    async def list(self) -> list[Equipment]:
        raise self._pending("list")

    async def get(self, equipment_id: str) -> Equipment:
        raise self._pending("get")

    async def create(self, data: EquipmentCreate) -> Equipment:
        raise self._pending("create")

    async def update(self, equipment: Equipment) -> Equipment:
        raise self._pending("update")

    async def delete(self, equipment_id: str) -> None:
        raise self._pending("delete")


class XanoTechnicianRepository(_XanoRepository):
    prefix = "technicians"

    async def list(self) -> list[Technician]:
        raise self._pending("list")


class XanoOrderRepository(_XanoRepository):
    prefix = "orders"

    async def list(self) -> list[ServiceOrder]:
        raise self._pending("list")

    async def get_by_code(self, code: str) -> ServiceOrder:
        raise self._pending("get_by_code")

    async def next_code(self) -> str:
        raise self._pending("next_code")

    async def create(self, order: ServiceOrder) -> ServiceOrder:
        raise self._pending("create")

    async def save(self, order: ServiceOrder) -> ServiceOrder:
        raise self._pending("save")


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
        technicians=XanoTechnicianRepository(client, registry),
        orders=XanoOrderRepository(client, registry),
    )
