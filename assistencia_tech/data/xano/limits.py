"""Limite de requisições do plano do Xano e cache curto de leituras.

O plano gratuito do Xano aceita poucas requisições por janela (10 a cada
20 segundos) e responde 429 acima disso. Cada tela administrativa precisa de
várias leituras, então o cliente HTTP:

- reaproveita por alguns segundos a resposta de leituras (GET) idênticas do
  mesmo usuário (``ResponseCache``); qualquer escrita limpa o cache inteiro, para
  que ninguém veja dados antigos depois de uma alteração;
- espaça as requisições para não passar do limite (``RequestPacer``).

O cache fica só na memória do servidor. Ele não afeta a segurança: o backend
confere perfil e conta ativa em toda chamada que chega a ele.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable
from typing import Any

Clock = Callable[[], float]
Sleep = Callable[[float], Any]

DEFAULT_MAX_REQUESTS = 10
DEFAULT_WINDOW_SECONDS = 20.0
DEFAULT_CACHE_SECONDS = 15.0


class RequestPacer:
    """Janela deslizante: no máximo ``max_requests`` a cada ``window`` segundos."""

    def __init__(
        self,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window: float = DEFAULT_WINDOW_SECONDS,
        *,
        clock: Clock = time.monotonic,
        sleep: Sleep = asyncio.sleep,
    ) -> None:
        self.max_requests = max_requests
        self.window = window
        self._clock = clock
        self._sleep = sleep
        self._sent: deque[float] = deque()
        self._lock = asyncio.Lock()

    def _forget_old(self, now: float) -> None:
        while self._sent and now - self._sent[0] >= self.window:
            self._sent.popleft()

    async def acquire(self) -> None:
        async with self._lock:
            now = self._clock()
            self._forget_old(now)
            if len(self._sent) >= self.max_requests:
                await self._sleep(self.window - (now - self._sent[0]) + 0.05)
                now = self._clock()
                self._forget_old(now)
            self._sent.append(now)

    async def wait_full_window(self) -> None:
        """Depois de um 429: espera a janela inteira antes de tentar de novo."""
        async with self._lock:
            await self._sleep(self.window)
            self._sent.clear()


class ResponseCache:
    def __init__(self, ttl: float = DEFAULT_CACHE_SECONDS, *, clock: Clock = time.monotonic) -> None:
        self.ttl = ttl
        self._clock = clock
        self._entries: dict[tuple, tuple[float, Any]] = {}

    def get(self, key: tuple) -> tuple[bool, Any]:
        entry = self._entries.get(key)
        if entry is None:
            return False, None
        stored_at, value = entry
        if self._clock() - stored_at > self.ttl:
            del self._entries[key]
            return False, None
        return True, value

    def put(self, key: tuple, value: Any) -> None:
        if self.ttl > 0:
            self._entries[key] = (self._clock(), value)

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)
