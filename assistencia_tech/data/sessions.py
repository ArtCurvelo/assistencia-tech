"""Sessões no servidor, identificadas por token opaco.

O navegador guarda apenas o token. Sessões expiram após ``IDLE_TIMEOUT`` sem
atividade e são revogadas no logout. Ficam em memória no processo.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..domain.clock import Clock, now_brt

IDLE_TIMEOUT = timedelta(hours=2)
TOKEN_BYTES = 32


@dataclass
class Session:
    user_id: str
    created_at: datetime
    last_seen_at: datetime


@dataclass(frozen=True)
class SessionLookup:
    user_id: str | None
    expired: bool = False


class SessionStore:
    def __init__(self, clock: Clock = now_brt, idle_timeout: timedelta = IDLE_TIMEOUT) -> None:
        self._clock = clock
        self._idle = idle_timeout
        self._sessions: dict[str, Session] = {}

    def create(self, user_id: str) -> str:
        token = secrets.token_urlsafe(TOKEN_BYTES)
        now = self._clock()
        self._sessions[token] = Session(user_id=user_id, created_at=now, last_seen_at=now)
        return token

    def resolve(self, token: str | None) -> SessionLookup:
        """Valida o token e renova a atividade; sessões expiradas são descartadas."""
        if not token:
            return SessionLookup(None)
        session = self._sessions.get(token)
        if session is None:
            return SessionLookup(None)
        now = self._clock()
        if now - session.last_seen_at > self._idle:
            del self._sessions[token]
            return SessionLookup(None, expired=True)
        session.last_seen_at = now
        return SessionLookup(session.user_id)

    def revoke(self, token: str | None) -> None:
        if token:
            self._sessions.pop(token, None)

    def __len__(self) -> int:
        return len(self._sessions)
