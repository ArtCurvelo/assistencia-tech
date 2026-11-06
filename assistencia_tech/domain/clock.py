"""Relógio e autoria usados pelos serviços (injetáveis nos testes)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

# Horário de Brasília (sem horário de verão desde 2019). Usa deslocamento fixo
# para não depender da base de fusos do sistema, ausente no Windows.
BRT = timezone(timedelta(hours=-3), "BRT")

DEFAULT_ACTOR = "Usuário demonstração"

Clock = Callable[[], datetime]


def now_brt() -> datetime:
    return datetime.now(BRT).replace(microsecond=0)


def format_datetime(value: datetime) -> str:
    return value.astimezone(BRT).strftime("%d/%m/%Y %H:%M")


def format_date(value: datetime) -> str:
    return value.astimezone(BRT).strftime("%d/%m/%Y")
