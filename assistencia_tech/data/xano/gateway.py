"""Adaptador Xano das interfaces de repositório.

Cada operação usa um contrato registrado em ``contracts.py`` e converte os
registros com ``mappers.py``. O JWT do usuário vem do contexto da requisição
(decisão D12). Técnicos são contas com perfil técnico, e o autocadastro cria
cliente e conta numa só chamada; por isso o gateway declara
``remote_accounts=True``.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...config import DATA_SOURCE_XANO, Settings
from ...models import Client, ClientCreate, Equipment, EquipmentCreate, Role, Technician, UserAccount
from ..errors import (
    AuthenticationError,
    ContractPendingError,
    NotFoundError,
    PermissionDeniedError,
    UnexpectedError,
    ValidationError,
)
from ..repositories import DataGateway
from ..request_context import issue_backend_token
from . import mappers
from .base import XanoRepository, group_ids, numeric_id
from .client import XanoClient
from .contracts import EndpointContract
from .inventory import XanoPartRepository
from .orders import XanoOrderRepository, XanoPortalRepository

INVALID_CREDENTIALS = "E-mail ou senha inválidos."
CLIENTS_PAGE_SIZE = 1000


class XanoClientRepository(XanoRepository):
    async def list(self) -> list[Client]:
        clients: list[Client] = []
        page = 1
        while True:
            result = await self._call("clients.list", params={"page": page, "per_page": CLIENTS_PAGE_SIZE})
            if not isinstance(result, dict):
                raise UnexpectedError(detail="clients.list: resposta sem paginação")
            clients.extend(mappers.client_from(r) for r in result.get("items") or [])
            next_page = result.get("nextPage")
            if not next_page or next_page == page:
                return clients
            page = int(next_page)

    async def get(self, client_id: str) -> Client:
        cid = numeric_id(client_id, "Cliente")
        return mappers.client_from(await self._record("clients.get", path_params={"cliente_id": cid}))

    async def create(self, data: ClientCreate) -> Client:
        return mappers.client_from(await self._record("clients.create", json=mappers.client_payload(data)))

    async def update(self, client: Client) -> Client:
        cid = numeric_id(client.id, "Cliente")
        record = await self._record(
            "clients.update", path_params={"cliente_id": cid}, json=mappers.client_payload(client)
        )
        return mappers.client_from(record)

    async def delete(self, client_id: str) -> None:
        await self._call("clients.delete", path_params={"cliente_id": numeric_id(client_id, "Cliente")})


class XanoEquipmentRepository(XanoRepository):
    async def list(self) -> list[Equipment]:
        return [mappers.equipment_from(r) for r in await self._list("equipment.list")]

    async def get(self, equipment_id: str) -> Equipment:
        eid = numeric_id(equipment_id, "Equipamento")
        return mappers.equipment_from(await self._record("equipment.get", path_params={"item_cliente_id": eid}))

    async def create(self, data: EquipmentCreate) -> Equipment:
        record = await self._record("equipment.create", json=mappers.equipment_payload(data))
        return mappers.equipment_from(record)

    async def update(self, equipment: Equipment) -> Equipment:
        eid = numeric_id(equipment.id, "Equipamento")
        record = await self._record(
            "equipment.update", path_params={"item_cliente_id": eid}, json=mappers.equipment_payload(equipment)
        )
        return mappers.equipment_from(record)

    async def delete(self, equipment_id: str) -> None:
        eid = numeric_id(equipment_id, "Equipamento")
        await self._call("equipment.delete", path_params={"item_cliente_id": eid})


class XanoTechnicianRepository(XanoRepository):
    async def list(self) -> list[Technician]:
        return [mappers.technician_from(r) for r in await self._list("technicians.list")]

    async def create(self, name: str, specialty: str) -> Technician:
        # No Xano o técnico nasce junto com a conta (``auth.create_user`` com especialidade).
        raise ContractPendingError(
            "No Xano, o técnico é cadastrado junto com a conta de acesso.",
            detail="technicians.create não se aplica com remote_accounts",
        )

    async def update(self, technician: Technician) -> Technician:
        uid = numeric_id(technician.id, "Técnico")
        record = await self._record(
            "users.update",
            path_params={"user_id": uid},
            json={"name": technician.name, "especialidade": technician.specialty, "ativo": technician.active},
        )
        return mappers.technician_from(record)


class XanoAuthProvider(XanoRepository):
    async def _me(self) -> UserAccount:
        return mappers.user_from(await self._record("auth.me"))

    async def _start_session(self, result: object) -> UserAccount:
        token = result.get("authToken") if isinstance(result, dict) else None
        if not isinstance(token, str) or not token:
            raise UnexpectedError(detail="resposta de autenticação sem authToken")
        issue_backend_token(token)
        return await self._me()

    async def authenticate(self, email: str, password: str) -> UserAccount:
        try:
            result = await self._call("auth.login", json={"email": email, "password": password})
        except (PermissionDeniedError, ValidationError, NotFoundError) as error:
            raise AuthenticationError(INVALID_CREDENTIALS, detail=error.detail) from None
        user = await self._start_session(result)
        if not user.active:
            raise AuthenticationError(INVALID_CREDENTIALS)
        return user

    async def get_user(self, user_id: str) -> UserAccount:
        me = await self._me()
        if me.id == user_id:
            return me
        for user in await self.list_users():
            if user.id == user_id:
                return user
        raise NotFoundError("Conta não encontrada.")

    async def email_in_use(self, email: str) -> bool:
        wanted = email.strip().casefold()
        return any(u.email.casefold() == wanted for u in await self.list_users())

    async def register_client(self, client: Client, password: str) -> UserAccount:
        raise ContractPendingError(
            "No Xano, o autocadastro usa signup_client.", detail="register_client não se aplica com remote_accounts"
        )

    async def signup_client(self, data: ClientCreate, password: str) -> UserAccount:
        result = await self._call("auth.signup_client", json={**mappers.client_payload(data), "password": password})
        return await self._start_session(result)

    async def list_users(self) -> list[UserAccount]:
        return [mappers.user_from(r) for r in await self._list("users.list")]

    async def create_user(
        self,
        name: str,
        email: str,
        role: Role,
        password: str,
        technician_id: str | None = None,
        specialty: str = "",
    ) -> UserAccount:
        payload = {
            "name": name,
            "email": email,
            "password": password,
            "role": mappers.ROLE_TO_XANO[role],
            "especialidade": specialty,
        }
        return mappers.user_from(await self._record("users.create", json=payload))

    async def update_user(self, user: UserAccount, new_password: str | None = None) -> UserAccount:
        payload: dict[str, object] = {"name": user.name, "role": mappers.ROLE_TO_XANO[user.role], "ativo": user.active}
        if new_password:
            payload["password"] = new_password
        uid = numeric_id(user.id, "Conta")
        return mappers.user_from(await self._record("users.update", path_params={"user_id": uid}, json=payload))


def build_xano_gateway(
    settings: Settings,
    *,
    client: XanoClient | None = None,
    registry: Mapping[str, EndpointContract] | None = None,
) -> DataGateway:
    client = client or XanoClient(settings.xano_base_url, settings.xano_timeout_seconds)
    groups = group_ids(settings)

    def repo(cls):
        return cls(client, groups, registry)

    return DataGateway(
        source=DATA_SOURCE_XANO,
        label="Backend Xano",
        is_demo=False,
        clients=repo(XanoClientRepository),
        equipment=repo(XanoEquipmentRepository),
        technicians=repo(XanoTechnicianRepository),
        orders=repo(XanoOrderRepository),
        auth=repo(XanoAuthProvider),
        portal=repo(XanoPortalRepository),
        parts=repo(XanoPartRepository),
        remote_accounts=True,
    )
