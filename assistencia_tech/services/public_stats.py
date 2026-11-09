"""Números públicos da página inicial com cache curto (mudança add-public-stats).

A página inicial é pública e pode receber muitas visitas; o Xano gratuito aceita
10 requisições a cada 20 segundos. Os números ficam guardados por 5 minutos no
processo. Em falha do backend, devolve ``None`` (a página mostra "—"), e a
falha não é guardada.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from ..data.errors import DataAccessError
from ..data.repositories import DataGateway
from ..models import PublicStats

CACHE_SECONDS = 300.0

_cache: dict[int, tuple[float, PublicStats]] = {}


async def public_stats(gateway: DataGateway, *, now: Callable[[], float] = time.monotonic) -> PublicStats | None:
    key = id(gateway)
    cached = _cache.get(key)
    if cached is not None and now() - cached[0] < CACHE_SECONDS:
        return cached[1]
    try:
        stats = await gateway.portal.public_stats()
    except DataAccessError:
        return None
    _cache[key] = (now(), stats)
    return stats


def clear_public_stats_cache() -> None:
    _cache.clear()
