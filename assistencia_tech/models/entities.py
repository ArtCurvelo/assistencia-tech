"""Modelos das entidades atuais do sistema.

Os campos refletem o estado atual da aplicação. A ampliação do domínio
(diagnóstico, peças, pagamentos, histórico) será feita em mudança própria.
"""

from __future__ import annotations

import re
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

ORDER_STATUSES: tuple[str, ...] = ("Recebido", "Em análise", "Em reparo", "Concluído")
EQUIPMENT_KINDS: tuple[str, ...] = ("Computador", "Notebook", "Console", "Celular", "Outro")
PHONE_NOT_INFORMED = "Não informado"

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class _Model(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)
    # Rótulos usados nas mensagens de validação exibidas ao usuário.
    field_labels: ClassVar[dict[str, str]] = {}


class ClientCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {"name": "Nome", "email": "E-mail", "phone": "Telefone"}

    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    phone: str = PHONE_NOT_INFORMED

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        if not _EMAIL_RE.match(value):
            raise ValueError("informe um e-mail válido")
        return value.lower()

    @field_validator("phone")
    @classmethod
    def _phone(cls, value: str) -> str:
        return value or PHONE_NOT_INFORMED


class Client(ClientCreate):
    id: str = Field(min_length=1)


class EquipmentCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {"client": "Cliente", "kind": "Tipo", "model": "Marca/modelo"}

    client: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    model: str = Field(min_length=1)


class Equipment(EquipmentCreate):
    id: str = Field(min_length=1)


class OrderCreate(_Model):
    field_labels: ClassVar[dict[str, str]] = {
        "client": "Cliente",
        "device": "Equipamento",
        "problem": "Problema relatado",
    }

    client: str = Field(min_length=1)
    device: str = Field(min_length=1)
    problem: str = Field(min_length=1)


class ServiceOrder(OrderCreate):
    field_labels: ClassVar[dict[str, str]] = {**OrderCreate.field_labels, "code": "Código", "status": "Status"}

    code: str = Field(min_length=1)
    status: str = ORDER_STATUSES[0]

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in ORDER_STATUSES:
            raise ValueError("status inválido")
        return value
