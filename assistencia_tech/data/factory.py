"""Criação do gateway de dados conforme a configuração do ambiente."""

from __future__ import annotations

from ..config import DATA_SOURCE_DEMO, Settings, load_settings
from .demo import build_demo_gateway
from .repositories import DataGateway
from .xano import build_xano_gateway

_gateway: DataGateway | None = None


def build_gateway(settings: Settings) -> DataGateway:
    """Cria o gateway da fonte configurada.

    Com a fonte Xano, uma configuração incompleta lança ``ConfigurationError``:
    os dados de demonstração nunca são usados como substitutos.
    """
    if settings.data_source == DATA_SOURCE_DEMO:
        return build_demo_gateway()
    return build_xano_gateway(settings)


def get_gateway() -> DataGateway:
    """Gateway único por processo, criado na primeira chamada."""
    global _gateway
    if _gateway is None:
        _gateway = build_gateway(load_settings())
    return _gateway


def reset_gateway() -> None:
    """Descarta o gateway atual (usado em testes e ao trocar a configuração)."""
    global _gateway
    _gateway = None
