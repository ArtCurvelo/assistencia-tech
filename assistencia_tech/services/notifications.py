"""Envio de avisos ao cliente (mudança add-client-self-service).

O envio acontece depois da operação e nunca a desfaz: qualquer falha vira um
registro no log. Sem ``BREVO_API_KEY`` e ``ASSISTENCIA_EMAIL_FROM``, ou no modo
demonstração, o ``NullNotifier`` não envia nada e nenhuma leitura extra é feita.
"""

from __future__ import annotations

import logging
from typing import Protocol

import httpx

from ..config import DATA_SOURCE_XANO, Settings, load_settings
from ..data.repositories import DataGateway
from ..data.xano.tls import system_ssl_context
from ..domain import notifications as rules
from ..domain import receipt
from ..models import Client, ServiceOrder

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


class Notifier(Protocol):
    enabled: bool

    async def send(self, to_email: str, to_name: str, message: rules.Message) -> bool: ...


class NullNotifier:
    enabled = False

    async def send(self, to_email: str, to_name: str, message: rules.Message) -> bool:
        return False


class BrevoNotifier:
    """E-mail transacional pela API HTTP do Brevo; a chave vem do ambiente, nunca do código."""

    enabled = True

    def __init__(self, api_key: str, sender_email: str, sender_name: str = rules.BRAND, *,
                 transport: httpx.AsyncBaseTransport | None = None, timeout: float = 10.0) -> None:
        self._api_key = api_key
        self._sender = {"name": sender_name, "email": sender_email}
        self._transport = transport
        self._timeout = timeout

    async def send(self, to_email: str, to_name: str, message: rules.Message) -> bool:
        payload = {"sender": self._sender, "to": [{"email": to_email, "name": to_name}],
                   "subject": message.subject, "textContent": message.text}
        kwargs = {"transport": self._transport} if self._transport else {"verify": system_ssl_context()}
        async with httpx.AsyncClient(timeout=self._timeout, **kwargs) as client:
            response = await client.post(BREVO_URL, json=payload,
                                         headers={"api-key": self._api_key, "accept": "application/json"})
        if response.status_code >= 400:
            # Nunca registra a chave nem o destinatário completo.
            logger.warning("Aviso por e-mail recusado pelo Brevo: HTTP %s", response.status_code)
            return False
        return True


def build_notifier(settings: Settings) -> Notifier:
    if settings.data_source == DATA_SOURCE_XANO and settings.brevo_api_key and settings.email_from:
        return BrevoNotifier(settings.brevo_api_key, settings.email_from)
    return NullNotifier()


_notifier: Notifier | None = None


def get_notifier() -> Notifier:
    global _notifier
    if _notifier is None:
        _notifier = build_notifier(load_settings())
    return _notifier


def set_notifier(notifier: Notifier | None) -> None:
    """Troca o notificador (testes) ou volta ao configurado no ambiente (``None``)."""
    global _notifier
    _notifier = notifier


async def notify_order_status(gateway: DataGateway, order: ServiceOrder, client: Client | None = None) -> bool:
    """Avisa o cliente do status atual da ordem. Nunca lança: a operação já foi concluída."""
    notifier = get_notifier()
    if not notifier.enabled:
        return False
    try:
        if client is None:
            client = await gateway.clients.get(order.client_id)
        if not rules.can_email(client):
            return False
        settings = load_settings()
        url = receipt.tracking_url(settings.public_url, order.code) if settings.public_url else ""
        message = rules.status_message(order, client.name, url, settings.store_address or "",
                                       settings.store_hours or "")
        return await notifier.send(client.email, client.name, message)
    except Exception:  # noqa: BLE001 - o aviso é acessório; nada aqui pode quebrar a operação
        logger.exception("Falha ao enviar o aviso da ordem %s", order.code)
        return False
