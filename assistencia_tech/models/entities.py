"""Entidades e objetos de valor do domínio.

Os modelos são imutáveis (``frozen``): alterações geram uma nova instância
com ``model_copy``. A ordem de serviço é um agregado que contém seus itens,
pagamentos e histórico.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, ClassVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

from ..domain.validators import normalize_cpf, normalize_phone, parse_brl

EQUIPMENT_KINDS: tuple[str, ...] = ("Computador", "Notebook", "Console", "Celular", "Tablet", "Outro")
PAYMENT_METHODS: tuple[str, ...] = ("Dinheiro", "PIX", "Cartão de débito", "Cartão de crédito")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

Money = Annotated[Decimal, BeforeValidator(parse_brl), Field(gt=0)]
Text = Annotated[str, Field(min_length=1)]


class OrderStatus(StrEnum):
    RECEIVED = "Recebido"
    ANALYSIS = "Em análise"
    AWAITING_APPROVAL = "Aguardando aprovação"
    REPAIR = "Em reparo"
    DONE = "Concluído"
    DELIVERED = "Entregue"
    CANCELLED = "Cancelado"


ORDER_STATUSES: tuple[str, ...] = tuple(status.value for status in OrderStatus)


class ItemKind(StrEnum):
    SERVICE = "Serviço"
    PART = "Peça"


class _Model(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)
    # Rótulos usados nas mensagens de validação exibidas ao usuário.
    field_labels: ClassVar[dict[str, str]] = {}


# ----------------------------------------------------------------------
# Clientes
# ----------------------------------------------------------------------
class ClientCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {"name": "Nome", "cpf": "CPF", "email": "E-mail", "phone": "Telefone"}

    name: Text
    cpf: Text
    email: Text
    phone: Text

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, value: str) -> str:
        return normalize_cpf(value)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        if not _EMAIL_RE.match(value):
            raise ValueError("informe um e-mail válido")
        return value.lower()

    @field_validator("phone")
    @classmethod
    def _phone(cls, value: str) -> str:
        return normalize_phone(value)


class Client(ClientCreate):
    id: Text


# ----------------------------------------------------------------------
# Técnicos
# ----------------------------------------------------------------------
class Technician(_Model):
    id: Text
    name: Text
    specialty: str = ""
    active: bool = True


# ----------------------------------------------------------------------
# Equipamentos
# ----------------------------------------------------------------------
class EquipmentCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {
        "client_id": "Cliente",
        "kind": "Tipo",
        "brand": "Marca",
        "model": "Modelo",
        "serial_number": "Número de série",
        "notes": "Observações",
    }

    client_id: Text
    kind: Text
    brand: Text
    model: Text
    serial_number: str = ""
    notes: str = ""

    @field_validator("kind")
    @classmethod
    def _kind(cls, value: str) -> str:
        if value not in EQUIPMENT_KINDS:
            raise ValueError(f"tipo inválido; use {', '.join(EQUIPMENT_KINDS)}")
        return value

    @field_validator("serial_number")
    @classmethod
    def _serial(cls, value: str) -> str:
        return value.upper()

    @property
    def description(self) -> str:
        return f"{self.kind} {self.brand} {self.model}"


class Equipment(EquipmentCreate):
    id: Text


def serial_key(serial: str) -> str:
    """Chave de comparação do número de série (sem espaços, sem caixa)."""
    return re.sub(r"\s", "", serial).casefold()


# ----------------------------------------------------------------------
# Itens, pagamentos e histórico
# ----------------------------------------------------------------------
class OrderItemCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {
        "kind": "Tipo do item",
        "description": "Descrição",
        "quantity": "Quantidade",
        "unit_price": "Valor",
    }

    kind: ItemKind
    description: Text
    quantity: int = Field(default=1, ge=1)
    unit_price: Money
    part_id: str = ""  # peça do catálogo de estoque; vazio para serviço e peça avulsa

    @field_validator("quantity", mode="before")
    @classmethod
    def _quantity(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip() or "1"
            if not value.isdigit():
                raise ValueError("informe uma quantidade inteira positiva")
            return int(value)
        return value


class OrderItem(OrderItemCreate):
    id: Text

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


class PaymentCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {"amount": "Valor do pagamento", "method": "Forma de pagamento"}

    amount: Money
    method: Text

    @field_validator("method")
    @classmethod
    def _method(cls, value: str) -> str:
        if value not in PAYMENT_METHODS:
            raise ValueError(f"forma de pagamento inválida; use {', '.join(PAYMENT_METHODS)}")
        return value


class Payment(PaymentCreate):
    id: Text
    paid_at: datetime


class HistoryEvent(_Model):
    at: datetime
    author: Text
    kind: Text
    description: Text
    to_status: str = ""  # preenchido nas mudanças de status


# ----------------------------------------------------------------------
# Ordem de serviço (agregado)
# ----------------------------------------------------------------------
def parse_optional_date(value: object) -> object:
    """Aceita ``AAAA-MM-DD`` (campo de data do navegador) ou ``dd/mm/aaaa``; vazio vira ``None``."""
    if value is None or isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError("informe uma data válida (dd/mm/aaaa)")


OptionalDate = Annotated[date | None, BeforeValidator(parse_optional_date)]


class OrderCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {
        "client_id": "Cliente",
        "equipment_id": "Equipamento",
        "problem": "Problema relatado",
        "due_date": "Previsão de entrega",
    }

    client_id: Text
    equipment_id: Text
    problem: Text
    due_date: OptionalDate = None  # sem previsão, a abertura usa +7 dias (add-deadlines-and-warranty)
    warranty_of: str = ""  # código da ordem original, nas ordens em garantia


class ServiceOrder(OrderCreate):
    code: Text
    status: OrderStatus = OrderStatus.RECEIVED
    opened_at: datetime
    updated_at: datetime
    technician_id: str | None = None
    diagnosis: str = ""
    cancel_reason: str = ""
    items: tuple[OrderItem, ...] = ()
    payments: tuple[Payment, ...] = ()
    history: tuple[HistoryEvent, ...] = ()


class PublicOrderView(_Model):
    """Projeção da OS para a consulta pública: sem dados pessoais nem valores."""

    code: str
    status: str
    equipment: str
    updated_at: datetime
    due_date: date | None = None
