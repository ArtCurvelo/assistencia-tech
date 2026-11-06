"""Serviço de aplicação de clientes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..data.errors import ValidationError
from ..data.repositories import DataGateway
from ..domain.validators import format_cpf
from ..domain.permissions import Permission as P
from ..domain.permissions import Principal, require
from ..models import Client, ClientCreate, Equipment, ServiceOrder, parse_model


@dataclass(frozen=True)
class ClientDetail:
    client: Client
    equipment: list[Equipment]
    orders: list[ServiceOrder]


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


class ClientService:
    def __init__(self, gateway: DataGateway, principal: Principal | None) -> None:
        self._gw = gateway
        self._principal = principal

    async def list(self) -> list[Client]:
        require(self._principal, P.CLIENTS_VIEW)
        return await self._gw.clients.list()

    async def get(self, client_id: str) -> Client:
        require(self._principal, P.CLIENTS_VIEW)
        return await self._gw.clients.get(client_id)

    async def _ensure_unique(self, data: ClientCreate, exclude_id: str | None = None) -> None:
        for other in await self._gw.clients.list():
            if other.id == exclude_id:
                continue
            if other.cpf == data.cpf:
                raise ValidationError(f"Já existe um cliente com o CPF {format_cpf(data.cpf)}.")
            if other.email == data.email:
                raise ValidationError(f"Já existe um cliente com o e-mail {data.email}.")

    async def create(self, form: Mapping[str, Any]) -> Client:
        require(self._principal, P.CLIENTS_MANAGE)
        data = parse_model(ClientCreate, form)
        await self._ensure_unique(data)
        return await self._gw.clients.create(data)

    async def update(self, client_id: str, form: Mapping[str, Any]) -> Client:
        require(self._principal, P.CLIENTS_MANAGE)
        await self._gw.clients.get(client_id)
        data = parse_model(ClientCreate, form)
        await self._ensure_unique(data, exclude_id=client_id)
        return await self._gw.clients.update(Client(id=client_id, **data.model_dump()))

    async def delete(self, client_id: str) -> Client:
        require(self._principal, P.CLIENTS_DELETE)
        client = await self._gw.clients.get(client_id)
        equipment = [e for e in await self._gw.equipment.list() if e.client_id == client_id]
        orders = [o for o in await self._gw.orders.list() if o.client_id == client_id]
        if equipment or orders:
            links = []
            if equipment:
                links.append(_plural(len(equipment), "equipamento", "equipamentos"))
            if orders:
                links.append(_plural(len(orders), "ordem de serviço", "ordens de serviço"))
            raise ValidationError(
                f"Não é possível excluir {client.name}: o cliente possui {' e '.join(links)} vinculados."
            )
        await self._gw.clients.delete(client_id)
        return client

    async def detail(self, client_id: str) -> ClientDetail:
        require(self._principal, P.CLIENTS_VIEW)
        client = await self._gw.clients.get(client_id)
        equipment = [e for e in await self._gw.equipment.list() if e.client_id == client_id]
        orders = sorted(
            (o for o in await self._gw.orders.list() if o.client_id == client_id),
            key=lambda o: o.opened_at,
            reverse=True,
        )
        return ClientDetail(client=client, equipment=equipment, orders=orders)
