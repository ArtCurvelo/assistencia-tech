"""Regras de gestão de colaboradores (funções puras)."""

from __future__ import annotations

from collections.abc import Iterable

from ..data.errors import ValidationError
from ..models import Role, UserAccount

STAFF_ROLE_VALUES: tuple[str, ...] = (Role.ADMIN.value, Role.ATTENDANT.value, Role.TECHNICIAN.value)


def parse_staff_role(value: str) -> Role:
    if value not in STAFF_ROLE_VALUES:
        raise ValidationError(f"Cargo inválido. Use: {', '.join(STAFF_ROLE_VALUES)}.")
    return Role(value)


def ensure_not_self(actor_id: str, target_id: str, message: str) -> None:
    if actor_id == target_id:
        raise ValidationError(message)


def ensure_admin_remains(
    users: Iterable[UserAccount], target_id: str, new_role: Role, new_active: bool
) -> None:
    """Simula a alteração e exige ao menos um administrador ativo."""
    remaining = 0
    for user in users:
        role, active = (new_role, new_active) if user.id == target_id else (user.role, user.active)
        if role == Role.ADMIN and active:
            remaining += 1
    if remaining == 0:
        raise ValidationError("É necessário manter ao menos um administrador ativo.")


def ensure_technician_can_leave(open_orders: int) -> None:
    if open_orders > 0:
        label = "ordem em aberto" if open_orders == 1 else "ordens em aberto"
        raise ValidationError(
            f"O técnico possui {open_orders} {label}; reatribua-as antes de mudar o cargo ou desativar a conta."
        )
