"""Avisos ao cliente sobre a ordem de serviço (mudança add-client-self-service).

Funções puras: quem pode receber e-mail, o texto de cada status e o link do
WhatsApp. O texto leva só o primeiro nome, o código, o status e o que acontece
em seguida — nunca valores, diagnóstico ou outros dados pessoais.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from ..models.entities import DELIVERY_COURIER, Client, OrderStatus, ServiceOrder
from .validators import only_digits

S = OrderStatus
BRAND = "Assistência TECH"
# Domínios reservados a testes e documentação (RFC 2606 e 6761): nunca recebem e-mail de verdade.
_RESERVED_SUFFIXES = (".test", ".invalid", ".example", ".localhost")
_RESERVED_DOMAINS = ("example.com", "example.org", "example.net")


@dataclass(frozen=True)
class Message:
    subject: str
    text: str


def can_email(client: Client | None) -> bool:
    if client is None or client.anonymized or "@" not in client.email:
        return False
    domain = client.email.rsplit("@", 1)[1].lower()
    return not (domain.endswith(_RESERVED_SUFFIXES) or domain in _RESERVED_DOMAINS)


def _what_happens(order: ServiceOrder, store_address: str, store_hours: str) -> str:
    status = order.status
    if status == S.REQUESTED:
        if order.delivery_mode == DELIVERY_COURIER:
            return ("Recebemos o seu pedido de atendimento. Vamos combinar a coleta por motoboy no endereço "
                    f"informado, no período: {order.pickup_period}.")
        where = f"Leve o equipamento a: {store_address}." if store_address else \
            "A assistência vai confirmar o endereço para você levar o equipamento."
        hours = f" Horário: {store_hours}." if store_address and store_hours else ""
        return f"Recebemos o seu pedido de atendimento. {where}{hours}"
    if status == S.RECEIVED:
        due = f" Previsão de entrega: {order.due_date:%d/%m/%Y}." if order.due_date else ""
        return f"Seu equipamento foi recebido e aguarda a análise técnica.{due}"
    return {
        S.ANALYSIS: "Um técnico está analisando o seu equipamento.",
        S.AWAITING_APPROVAL: "O orçamento está pronto. Entre no portal para aprovar ou recusar.",
        S.REPAIR: "O orçamento foi aprovado e o reparo está em andamento.",
        S.DONE: "O reparo foi concluído e o equipamento está pronto para retirada.",
        S.DELIVERED: "Equipamento entregue. O serviço tem garantia de 90 dias. Avalie o atendimento no portal.",
        S.CANCELLED: "A ordem de serviço foi cancelada. Em caso de dúvida, fale com a assistência.",
    }[status]


def status_message(order: ServiceOrder, client_name: str, tracking_url: str = "", store_address: str = "",
                   store_hours: str = "") -> Message:
    first = (client_name or "").split(" ")[0]
    greeting = f"Olá, {first}!" if first else "Olá!"
    lines = [greeting, "", f"Ordem {order.code} — {order.status.value}",
             _what_happens(order, store_address, store_hours)]
    if tracking_url:
        lines += ["", f"Acompanhe: {tracking_url}"]
    lines += ["", BRAND]
    return Message(f"{BRAND} — {order.code}: {order.status.value}", "\n".join(lines))


def whatsapp_link(phone: str, text: str) -> str:
    """Link que abre a conversa com a mensagem pronta; vazio se o telefone não for um número brasileiro válido."""
    digits = only_digits(phone or "")
    if len(digits) not in (10, 11):
        return ""
    return f"https://wa.me/55{digits}?text={quote(text)}"
