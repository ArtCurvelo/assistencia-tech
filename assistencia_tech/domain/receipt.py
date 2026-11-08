"""Comprovante da ordem de serviço com QR code (mudança add-order-receipt).

Regras puras: tipo do comprovante, endereço da consulta pública e o QR code
em SVG, gerado localmente pelo ``segno`` (nenhum serviço externo recebe o
código da ordem).
"""

from __future__ import annotations

import re
from urllib.parse import quote, urlsplit

import segno

from ..models.entities import OrderStatus, ServiceOrder

RECEIPT_ENTRY = "Comprovante de entrada"
RECEIPT_DELIVERY = "Comprovante de entrega"
TRACKING_PATH = "/consulta/"

_CODE_RE = re.compile(r"^OS-\d{4}-\d{5,}$")


def receipt_kind(order: ServiceOrder) -> str:
    return RECEIPT_DELIVERY if order.status == OrderStatus.DELIVERED else RECEIPT_ENTRY


def normalize_code(code: str) -> str | None:
    """Código no formato ``OS-AAAA-NNNNN`` em maiúsculas, ou ``None`` se o formato não confere."""
    cleaned = (code or "").strip().upper()
    return cleaned if _CODE_RE.match(cleaned) else None


def public_base_url(configured: str | None, request_origin: str) -> str:
    """Endereço público: o configurado ou, sem ele, a origem (esquema + host) da requisição."""
    if configured:
        return configured.rstrip("/")
    parts = urlsplit(request_origin or "")
    if parts.scheme in ("http", "https") and parts.netloc:
        return f"{parts.scheme}://{parts.netloc}"
    return ""


def tracking_url(base_url: str, code: str) -> str:
    return f"{base_url.rstrip('/')}{TRACKING_PATH}{quote(code, safe='')}"


def qr_svg_data_uri(content: str) -> str:
    """QR code do conteúdo como imagem SVG embutida (``data:image/svg+xml``)."""
    qr = segno.make(content, error="m", micro=False)
    return qr.svg_data_uri(scale=4, border=2, dark="#000", light="#fff")
