"""Cliente HTTP genérico para o backend Xano.

Este módulo não conhece nenhum endpoint: executa requisições descritas por
contratos registrados em ``contracts.py`` e traduz falhas para a hierarquia
de ``DataAccessError``.

Cada grupo de API do Xano tem seu próprio endereço (``{instância}/api:{grupo}``).
O JWT do usuário vem do contexto da requisição (``data.request_context``).

Mensagens do servidor: só são exibidas ao usuário as mensagens das
pré-condições do backend em XanoScript (``precondition``), que o Xano devolve
com ``"payload": ""``. Erros nativos do Xano (em inglês, com ``payload``
objeto ou sem ``payload``) ficam apenas no log, e o usuário vê a mensagem
padrão em português.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..errors import (
    AuthenticationError,
    ConfigurationError,
    DataAccessError,
    NotFoundError,
    PermissionDeniedError,
    ServiceUnavailableError,
    UnexpectedError,
    ValidationError,
)
from ..request_context import current_backend_token
from .limits import RequestPacer, ResponseCache
from .tls import system_ssl_context

logger = logging.getLogger(__name__)

_UNAVAILABLE_STATUSES = {408, 429}


def server_message(body: Any) -> str | None:
    """Mensagem de uma pré-condição do backend (segura para o usuário) ou ``None``."""
    if not isinstance(body, dict) or body.get("payload", None) != "":
        return None
    message = body.get("message")
    return message.strip() if isinstance(message, str) and message.strip() else None


def error_for_status(
    status_code: int, *, detail: str | None = None, message: str | None = None
) -> DataAccessError | None:
    """Converte um status HTTP em erro de acesso a dados (``None`` para sucesso)."""
    if 200 <= status_code < 300:
        return None
    if status_code in (400, 422):
        return ValidationError(message, detail=detail)
    if status_code == 401:
        return AuthenticationError(detail=detail)
    if status_code == 403:
        return PermissionDeniedError(message, detail=detail)
    if status_code == 404:
        return NotFoundError(message, detail=detail)
    if status_code in _UNAVAILABLE_STATUSES or status_code >= 500:
        return ServiceUnavailableError(detail=detail)
    return UnexpectedError(detail=detail)


def _json_or_none(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


class XanoClient:
    def __init__(
        self,
        base_url: str | None,
        timeout_seconds: float,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        pacer: RequestPacer | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        if not base_url:
            raise ConfigurationError(
                "A fonte de dados Xano foi selecionada, mas XANO_BASE_URL não está configurada. "
                "Configure o endereço da instância; os dados de demonstração não serão usados no lugar."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._transport = transport
        # ``is None`` (e não ``or``): um cache vazio tem len() == 0 e seria descartado.
        self._pacer = RequestPacer() if pacer is None else pacer
        self._cache = ResponseCache() if cache is None else cache

    def url_for(self, group: str, path: str) -> str:
        return f"{self.base_url}/api:{group}{path}"

    async def request(
        self,
        method: str,
        group: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        authenticated: bool = True,
    ) -> Any:
        """Executa a requisição e retorna o JSON decodificado (ou ``None`` sem corpo).

        Leituras idênticas do mesmo usuário são reaproveitadas por alguns
        segundos; escritas limpam o cache. Um 429 do Xano espera a janela do
        limite e tenta uma única vez de novo.
        """
        headers: dict[str, str] = {}
        token = None
        if authenticated:
            token = current_backend_token()
            if not token:
                raise AuthenticationError(detail=f"{method} {path}: sem token do backend na sessão")
            headers["Authorization"] = f"Bearer {token}"
        url = self.url_for(group, path)
        is_read = method.upper() == "GET"
        key = (token, url, tuple(sorted((params or {}).items())))
        if is_read:
            hit, cached = self._cache.get(key)
            if hit:
                return cached
        else:
            self._cache.clear()

        result = await self._send(method, url, path, group, params, json, headers, retry=True)
        if is_read:
            self._cache.put(key, result)
        else:
            self._cache.clear()
        return result

    async def _send(self, method, url, path, group, params, json, headers, *, retry: bool) -> Any:
        await self._pacer.acquire()
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self._transport,
                verify=system_ssl_context(),
            ) as http:
                response = await http.request(method, url, params=params, json=json, headers=headers)
        except httpx.TimeoutException as exc:
            logger.warning("Tempo limite excedido: %s %s", method, path)
            raise ServiceUnavailableError(detail=f"timeout: {exc!r}") from exc
        except httpx.TransportError as exc:
            logger.warning("Falha de conexão: %s %s (%r)", method, path, exc)
            raise ServiceUnavailableError(detail=f"transport: {exc!r}") from exc

        if response.status_code == 429 and retry:
            logger.warning("Limite de requisições do Xano atingido; aguardando a janela: %s %s", method, path)
            await self._pacer.wait_full_window()
            return await self._send(method, url, path, group, params, json, headers, retry=False)

        body = _json_or_none(response) if response.content else None
        detail = f"{method} api:{group}{path} -> {response.status_code}"
        if not 200 <= response.status_code < 300 and isinstance(body, dict):
            detail = f"{detail} ({body.get('code')}: {body.get('message')})"
        error = error_for_status(response.status_code, detail=detail, message=server_message(body))
        if error is not None:
            logger.warning("Resposta de erro do Xano: %s", error.detail)
            raise error

        if not response.content:
            return None
        if body is None:
            raise UnexpectedError(detail=f"resposta não-JSON em {method} {path}")
        return body
