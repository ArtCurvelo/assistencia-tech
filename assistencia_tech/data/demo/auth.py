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

    async def register_client(self, client: Client, password: str) -> UserAccount:
        if await self.email_in_use(client.email):
            raise ValidationError(f"Já existe uma conta com o e-mail {client.email}.")
        next_id = str(max((int(u.id) for u in self.users if u.id.isdigit()), default=0) + 1)
        user = UserAccount(
            id=next_id,
            name=client.name,
            email=client.email,
            role=Role.CLIENT,
            password_hash=hash_password(password, iterations=self._iterations),
            client_id=client.id,
        )
        self.users.append(user)
        return user
