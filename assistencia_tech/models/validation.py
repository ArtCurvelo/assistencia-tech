"""Conversão de erros do Pydantic em erros compreensíveis para o usuário."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

import pydantic

from ..data.errors import ValidationError

M = TypeVar("M", bound=pydantic.BaseModel)


def _message_for(model_cls: type[pydantic.BaseModel], error: Mapping[str, Any]) -> str:
    labels: dict[str, str] = getattr(model_cls, "field_labels", {})
    loc = error.get("loc") or ("",)
    field = str(loc[0])
    label = labels.get(field, field or "Campo")
    kind = error.get("type", "")
    if kind in {"missing", "string_too_short"}:
        return f"Preencha o campo obrigatório: {label}."
    if kind == "value_error":
        reason = str(error.get("ctx", {}).get("error", "valor inválido"))
        return f"{label}: {reason}."
    return f"{label}: valor inválido."


def parse_model(model_cls: type[M], data: Mapping[str, Any]) -> M:
    """Valida ``data`` com ``model_cls`` e lança ``ValidationError`` legível."""
    try:
        return model_cls.model_validate(dict(data))
    except pydantic.ValidationError as exc:
        messages = [_message_for(model_cls, err) for err in exc.errors()]
        raise ValidationError(" ".join(dict.fromkeys(messages)), detail=str(exc)) from exc
