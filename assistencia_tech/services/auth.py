"""Serviço de autenticação: login, logout, sessão e cadastro de cliente.

Sessões e limitador de tentativas são únicos por processo (em memória),
como os dados do modo demonstração.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..data.errors import AuthenticationError, NotFoundError, ValidationError
from ..data.repositories import DataGateway
from ..data.sessions import SessionStore
from ..domain.login_throttle import LoginThrottle
from ..domain.passwords import check_password_policy
from ..domain.permissions import Principal, principal_from, system_principal
from ..models import ClientCreate, parse_model
from .clients import ClientService

INVALID_CREDENTIALS = "E-mail ou senha inválidos."
SESSION_EXPIRED = "Sua sessão expirou por inatividade. Entre novamente."

_sessions = SessionStore()
_throttle = LoginThrottle()


def reset_auth_state(sessions: SessionStore | None = None, throttle: LoginThrottle | None = None) -> None:
    """Recria sessões e limitador (usado nos testes)."""
    global _sessions, _throttle
    # ``is None`` (e não ``or``): um SessionStore vazio tem len() == 0 e seria descartado.
    _sessions = SessionStore() if sessions is None else sessions
    _throttle = LoginThrottle() if throttle is None else throttle


@dataclass(frozen=True)
class SessionResult:
    principal: Principal | None
    expired: bool = False


class AuthService:
    def __init__(self, gateway: DataGateway) -> None:
        self._gw = gateway

    async def login(self, email: str, password: str) -> tuple[str, Principal]:
        email = (email or "").strip()
        if not email or not password:
            raise ValidationError("Informe o e-mail e a senha.")
        minutes = _throttle.remaining_minutes(email)
        if minutes:
            raise AuthenticationError(
                f"Acesso temporariamente bloqueado por excesso de tentativas. Tente novamente em {minutes} minuto(s)."
            )
        try:
            user = await self._gw.auth.authenticate(email, password)
        except AuthenticationError:
            _throttle.register_failure(email)
            raise AuthenticationError(INVALID_CREDENTIALS) from None
        _throttle.register_success(email)
        return _sessions.create(user.id), principal_from(user)

    async def resolve(self, token: str | None) -> SessionResult:
        lookup = _sessions.resolve(token)
        if lookup.user_id is None:
            return SessionResult(None, expired=lookup.expired)
        try:
            user = await self._gw.auth.get_user(lookup.user_id)
        except NotFoundError:
            _sessions.revoke(token)
            return SessionResult(None)
        if not user.active:
            _sessions.revoke(token)
            return SessionResult(None)
        return SessionResult(principal_from(user))

    def logout(self, token: str | None) -> None:
        _sessions.revoke(token)

    async def register_client(self, form: Mapping[str, Any]) -> tuple[str, Principal]:
        password = str(form.get("password", ""))
        if password != str(form.get("password_confirm", "")):
            raise ValidationError("As senhas não conferem.")
        check_password_policy(password)
        data = parse_model(ClientCreate, form)
        if await self._gw.auth.email_in_use(data.email):
            raise ValidationError(f"Já existe uma conta com o e-mail {data.email}.")
        # O cadastro público é um fluxo do sistema: usa as mesmas regras do cadastro de clientes.
        client = await ClientService(self._gw, system_principal("Autoatendimento")).create(data.model_dump())
        user = await self._gw.auth.register_client(client, password)
        return _sessions.create(user.id), principal_from(user)
