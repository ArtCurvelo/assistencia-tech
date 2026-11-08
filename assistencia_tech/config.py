"""Configuração da aplicação lida de variáveis de ambiente.

Nenhuma credencial é definida aqui: o acesso ao Xano usa o token de cada
usuário, obtido no login. ``XANO_BASE_URL`` é o endereço da instância e cada
grupo de API (``api:<grupo>``) tem um identificador configurável; os padrões
são os canônicos do backend em XanoScript da pasta ``xano/``.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from .data.errors import ConfigurationError

DATA_SOURCE_DEMO = "demo"
DATA_SOURCE_XANO = "xano"
VALID_DATA_SOURCES = (DATA_SOURCE_DEMO, DATA_SOURCE_XANO)
DEFAULT_TIMEOUT_SECONDS = 10.0

ENV_DATA_SOURCE = "ASSISTENCIA_DATA_SOURCE"
ENV_XANO_BASE_URL = "XANO_BASE_URL"
ENV_XANO_TIMEOUT = "XANO_TIMEOUT_SECONDS"
ENV_XANO_GROUP_AUTH = "XANO_GROUP_AUTH"
ENV_XANO_GROUP_CLIENTE = "XANO_GROUP_CLIENTE"
ENV_XANO_GROUP_OS = "XANO_GROUP_OS"
ENV_PUBLIC_URL = "ASSISTENCIA_PUBLIC_URL"  # endereço público usado no QR code dos comprovantes

DEFAULT_GROUP_AUTH = "assistencia-tech-auth"
DEFAULT_GROUP_CLIENTE = "assistencia-tech-cliente"
DEFAULT_GROUP_OS = "assistencia-tech-os"


@dataclass(frozen=True)
class Settings:
    data_source: str = DATA_SOURCE_DEMO
    xano_base_url: str | None = None
    xano_timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    xano_group_auth: str = DEFAULT_GROUP_AUTH
    xano_group_cliente: str = DEFAULT_GROUP_CLIENTE
    xano_group_os: str = DEFAULT_GROUP_OS
    public_url: str | None = None


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_timeout(raw: str | None) -> float:
    if raw is None:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = float(raw)
    except ValueError:
        timeout = -1.0
    if timeout <= 0:
        raise ConfigurationError(
            f"{ENV_XANO_TIMEOUT} deve ser um número positivo de segundos (recebido: '{raw}')."
        )
    return timeout


def _parse_public_url(raw: str | None) -> str | None:
    if raw is None:
        return None
    if not raw.startswith(("http://", "https://")):
        raise ConfigurationError(f"{ENV_PUBLIC_URL} deve começar com http:// ou https:// (recebido: '{raw}').")
    return raw.rstrip("/")


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Lê as configurações do ambiente (``os.environ`` por padrão)."""
    env = os.environ if env is None else env

    source = (_clean(env.get(ENV_DATA_SOURCE)) or DATA_SOURCE_DEMO).lower()
    if source not in VALID_DATA_SOURCES:
        accepted = ", ".join(VALID_DATA_SOURCES)
        raise ConfigurationError(
            f"Fonte de dados desconhecida em {ENV_DATA_SOURCE}: '{source}'. Valores aceitos: {accepted}."
        )

    base_url = _clean(env.get(ENV_XANO_BASE_URL))
    if base_url is not None:
        base_url = base_url.rstrip("/")

    return Settings(
        data_source=source,
        xano_base_url=base_url,
        xano_timeout_seconds=_parse_timeout(_clean(env.get(ENV_XANO_TIMEOUT))),
        xano_group_auth=_clean(env.get(ENV_XANO_GROUP_AUTH)) or DEFAULT_GROUP_AUTH,
        xano_group_cliente=_clean(env.get(ENV_XANO_GROUP_CLIENTE)) or DEFAULT_GROUP_CLIENTE,
        xano_group_os=_clean(env.get(ENV_XANO_GROUP_OS)) or DEFAULT_GROUP_OS,
        public_url=_parse_public_url(_clean(env.get(ENV_PUBLIC_URL))),
    )
