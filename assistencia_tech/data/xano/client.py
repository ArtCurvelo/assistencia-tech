"""Cliente HTTP genérico para o backend Xano.

Este módulo não conhece nenhum endpoint: ele apenas executa requisições
descritas por contratos registrados em ``contracts.py`` e traduz falhas
para a hierarquia de ``DataAccessError``. A classificação usa somente o
código de status HTTP, pois o formato de erro do Xano ainda não foi
documentado para este projeto.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..errors import (
    ConfigurationError,
    DataAccessError,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
    UnexpectedError,
    ValidationError,
)

logger = logging.getLogger(__name__)

_UNAVAILABLE_STATUSES = {408, 429}


def error_for_status(status_code: int, *, detail: str | None = None) -> DataAccessError | None:
    """Converte um status HTTP em erro de acesso a dados (``None`` para sucesso)."""
    if 200 <= status_code < 300:
        return None
    if status_code in (400, 422):
        return ValidationError(detail=detail)
    if status_code in (401, 403):
        return UnauthorizedError(detail=detail)
    if status_code == 404:
        return NotFoundError(detail=detail)
    if status_code in _UNAVAILABLE_STATUSES or status_code >= 500:
        return ServiceUnavailableError(detail=detail)
    return UnexpectedError(detail=detail)


class XanoClient:
    def __init__(
        self,
        base_url: str | None,
        timeout_seconds: float,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not base_url:
            raise ConfigurationError(
                "A fonte de dados Xano foi selecionada, mas XANO_BASE_URL não está configurada. "
                "Configure o endereço da API; os dados de demonstração não serão usados no lugar."
            )
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Executa a requisição e retorna o JSON decodificado (ou ``None`` sem corpo)."""
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                transport=self._transport,
            ) as http:
                response = await http.request(method, path, params=params, json=json, headers=headers)
        except httpx.TimeoutException as exc:
            logger.warning("Tempo limite excedido: %s %s", method, path)
            raise ServiceUnavailableError(detail=f"timeout: {exc!r}") from exc
        except httpx.TransportError as exc:
            logger.warning("Falha de conexão: %s %s (%r)", method, path, exc)
            raise ServiceUnavailableError(detail=f"transport: {exc!r}") from exc

        error = error_for_status(response.status_code, detail=f"{method} {path} -> {response.status_code}")
        if error is not None:
            logger.warning("Resposta de erro do Xano: %s", error.detail)
            raise error

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise UnexpectedError(detail=f"resposta não-JSON em {method} {path}") from exc
