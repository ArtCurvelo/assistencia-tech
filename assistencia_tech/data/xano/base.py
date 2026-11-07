"""Base dos repositórios Xano: resolve o contrato e executa a chamada."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...config import Settings
from ..errors import NotFoundError, UnexpectedError
from .client import XanoClient
from .contracts import GROUP_AUTH, GROUP_CLIENTE, GROUP_OS, EndpointContract, require_contract


def group_ids(settings: Settings) -> dict[str, str]:
    """Identificador real (``api:<id>``) de cada grupo lógico."""
    return {
        GROUP_AUTH: settings.xano_group_auth,
        GROUP_CLIENTE: settings.xano_group_cliente,
        GROUP_OS: settings.xano_group_os,
    }


def numeric_id(value: str, label: str) -> int:
    """Ids do Xano são inteiros; outro valor equivale a registro inexistente."""
    text = (value or "").strip()
    if not text.isdigit() or int(text) <= 0:
        raise NotFoundError(f"{label} não encontrado.")
    return int(text)


class XanoRepository:
    def __init__(
        self,
        client: XanoClient,
        groups: Mapping[str, str],
        registry: Mapping[str, EndpointContract] | None = None,
    ) -> None:
        self._client = client
        self._groups = groups
        self._registry = registry

    async def _call(
        self,
        operation: str,
        *,
        path_params: Mapping[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        contract = require_contract(operation, self._registry)
        path = contract.path.format(**(path_params or {}))
        return await self._client.request(
            contract.method,
            self._groups[contract.group],
            path,
            params=params,
            json=json,
            authenticated=not contract.public,
        )

    async def _record(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        result = await self._call(operation, **kwargs)
        if not isinstance(result, dict):
            raise UnexpectedError(detail=f"{operation}: esperado um objeto, recebido {type(result).__name__}")
        return result

    async def _list(self, operation: str, **kwargs: Any) -> list[dict[str, Any]]:
        result = await self._call(operation, **kwargs)
        if isinstance(result, dict) and isinstance(result.get("items"), list):
            result = result["items"]
        if not isinstance(result, list):
            raise UnexpectedError(detail=f"{operation}: esperada uma lista, recebido {type(result).__name__}")
        return [r for r in result if isinstance(r, dict)]
