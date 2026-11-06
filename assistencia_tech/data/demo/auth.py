"""Provedor de autenticação do modo demonstração (contas em memória)."""

from __future__ import annotations

from ...domain.passwords import DEFAULT_ITERATIONS, hash_password, verify_password
from ...models import Client, Role, UserAccount
from ..errors import AuthenticationError, NotFoundError, ValidationError

INVALID_CREDENTIALS = "E-mail ou senha inválidos."

# Hash de referência para equalizar o tempo de resposta quando o e-mail não
# existe (evita descobrir contas pelo tempo de resposta).
_DUMMY_HASH = (
    "pbkdf2_sha256$600000$3e492aa05c53ac386f9ef2c449241485$"
    "0000000000000000000000000000000000000000000000000000000000000000"
)


class DemoAuthProvider:
    def __init__(self, users: list[UserAccount], *, iterations: int = DEFAULT_ITERATIONS) -> None:
        self.users = list(users)
        self._iterations = iterations

    def _by_email(self, email: str) -> UserAccount | None:
        wanted = email.strip().casefold()
        return next((u for u in self.users if u.email.casefold() == wanted), None)

    async def authenticate(self, email: str, password: str) -> UserAccount:
        user = self._by_email(email)
        if user is None:
            verify_password(password, _DUMMY_HASH)
            raise AuthenticationError(INVALID_CREDENTIALS)
        if not verify_password(password, user.password_hash) or not user.active:
            raise AuthenticationError(INVALID_CREDENTIALS)
        return user

    async def get_user(self, user_id: str) -> UserAccount:
        user = next((u for u in self.users if u.id == user_id), None)
        if user is None:
            raise NotFoundError("Conta não encontrada.")
        return user

    async def email_in_use(self, email: str) -> bool:
        return self._by_email(email) is not None

    def _next_id(self) -> str:
        return str(max((int(u.id) for u in self.users if u.id.isdigit()), default=0) + 1)

    async def register_client(self, client: Client, password: str) -> UserAccount:
        if await self.email_in_use(client.email):
            raise ValidationError(f"Já existe uma conta com o e-mail {client.email}.")
        user = UserAccount(
            id=self._next_id(),
            name=client.name,
            email=client.email,
            role=Role.CLIENT,
            password_hash=hash_password(password, iterations=self._iterations),
            client_id=client.id,
        )
        self.users.append(user)
        return user

    async def list_users(self) -> list[UserAccount]:
        return list(self.users)

    async def create_user(
        self, name: str, email: str, role: Role, password: str, technician_id: str | None = None
    ) -> UserAccount:
        if await self.email_in_use(email):
            raise ValidationError(f"Já existe uma conta com o e-mail {email}.")
        user = UserAccount(
            id=self._next_id(),
            name=name,
            email=email,
            role=role,
            password_hash=hash_password(password, iterations=self._iterations),
            technician_id=technician_id,
        )
        self.users.append(user)
        return user

    async def update_user(self, user: UserAccount, new_password: str | None = None) -> UserAccount:
        current = await self.get_user(user.id)
        changes = {"name": user.name, "role": user.role, "active": user.active, "technician_id": user.technician_id}
        if new_password is not None:
            changes["password_hash"] = hash_password(new_password, iterations=self._iterations)
        updated = current.model_copy(update=changes)
        self.users = [updated if u.id == user.id else u for u in self.users]
        return updated
