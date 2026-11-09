"""Interfaces internas de persistência.

Os repositórios apenas gravam e leem dados; regras de negócio ficam em
``domain`` e a orquestração em ``services``. Cada fonte de dados
(demonstração, Xano) fornece uma implementação compatível.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..models import (
    Client,
    ClientCreate,
    Equipment,
    EquipmentCreate,
    Part,
    PartCreate,
    PublicOrderView,
    PublicStats,
    Role,
    ServiceOrder,
    StockMovement,
    Technician,
    UserAccount,
)


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
    async def list(self) -> list[Technician]:
        """Todos os técnicos, inclusive inativos (necessários para o histórico)."""
        ...

    async def create(self, name: str, specialty: str) -> Technician: ...

    async def update(self, technician: Technician) -> Technician: ...


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


@runtime_checkable
class AuthProvider(Protocol):
    """Autenticação e contas de acesso (credenciais nunca saem deste provedor)."""

    async def authenticate(self, email: str, password: str) -> UserAccount:
        """Retorna a conta ou lança ``AuthenticationError`` com mensagem genérica."""
        ...

    async def get_user(self, user_id: str) -> UserAccount:
        """Retorna a conta ou lança ``NotFoundError``."""
        ...

    async def email_in_use(self, email: str) -> bool: ...

    async def register_client(self, client: Client, password: str) -> UserAccount:
        """Cria a conta com perfil Cliente associada a ``client``."""
        ...

    async def list_users(self) -> list[UserAccount]: ...

    async def create_user(
        self,
        name: str,
        email: str,
        role: Role,
        password: str,
        technician_id: str | None = None,
        specialty: str = "",
    ) -> UserAccount:
        """Cria uma conta de colaborador; o hash é calculado pelo provedor.

        ``specialty`` é usado por provedores em que o técnico é a própria conta.
        """
        ...

    async def update_user(self, user: UserAccount, new_password: str | None = None) -> UserAccount:
        """Atualiza dados da conta e, opcionalmente, define uma nova senha."""
        ...


@runtime_checkable
class PartRepository(Protocol):
    """Catálogo de peças. A quantidade só muda por movimentações (entradas e itens de ordens)."""

    async def list(self) -> list[Part]: ...

    async def get(self, part_id: str) -> Part:
        """Retorna a peça ou lança ``NotFoundError``."""
        ...

    async def create(self, data: PartCreate) -> Part: ...

    async def update(self, part: Part) -> Part:
        """Atualiza código, nome, preço, mínimo e situação; nunca a quantidade."""
        ...

    async def restock(self, part_id: str, quantity: int, author: str, note: str = "") -> Part: ...

    async def movements(self) -> list[StockMovement]:
        """Movimentações da mais recente para a mais antiga."""
        ...


@runtime_checkable
class PortalRepository(Protocol):
    """Projeções para o cliente e para a consulta pública (decisão D14)."""

    async def client_account(self, client_id: str) -> Client:
        """Cadastro do cliente da conta autenticada."""
        ...

    async def client_orders(self, client_id: str) -> list[tuple[ServiceOrder, Equipment | None]]:
        """Somente as ordens do cliente, com o equipamento de cada uma."""
        ...

    async def public_order(self, code: str) -> PublicOrderView:
        """Status público da ordem, sem dados pessoais nem valores; ou ``NotFoundError``."""
        ...

    async def public_stats(self) -> PublicStats:
        """Contagens agregadas para a página inicial (entregues, em atendimento, avaliações)."""
        ...

    async def save_client_decision(
        self, client_id: str, order: ServiceOrder, approve: bool, reason: str
    ) -> ServiceOrder:
        """Grava a decisão do cliente sobre o orçamento; ``order`` já vem atualizada pelo domínio."""
        ...

    async def save_rating(self, client_id: str, order: ServiceOrder) -> ServiceOrder:
        """Grava a avaliação (``order.rating``) de uma ordem do cliente; recusa se já houver uma."""
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
    auth: AuthProvider
    portal: PortalRepository
    parts: PartRepository
    # Com contas remotas (Xano), técnicos são contas com perfil técnico e o
    # autocadastro cria cliente e conta numa só chamada (``auth.signup_client``).
    remote_accounts: bool = False
