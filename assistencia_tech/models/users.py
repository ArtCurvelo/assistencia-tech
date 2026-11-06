"""Contas de acesso. Separadas de ``Client``: colaboradores não são clientes
e credenciais não se misturam a dados de negócio."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    ADMIN = "Administrador"
    ATTENDANT = "Atendente"
    TECHNICIAN = "Técnico"
    CLIENT = "Cliente"


class UserAccount(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    role: Role
    # Nunca exibido nem registrado: ``repr=False`` evita vazamento em logs.
    password_hash: str = Field(min_length=1, repr=False)
    client_id: str | None = None
    technician_id: str | None = None
    active: bool = True
