"""Serviço de gestão de colaboradores (somente Administrador)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..data.errors import NotFoundError, ValidationError
from ..data.repositories import DataGateway
from ..domain.order_workflow import OPEN_STATUSES
from ..domain.passwords import check_password_policy
from ..domain.permissions import STAFF_ROLES, Permission, Principal, require
from ..domain.staff_rules import (
    ensure_admin_remains,
    ensure_not_self,
    ensure_technician_can_leave,
    parse_staff_role,
)
from ..models import Role, Technician, UserAccount

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class StaffMember:
    user: UserAccount
    technician: Technician | None


def _text(form: Mapping[str, Any], key: str) -> str:
    return str(form.get(key, "") or "").strip()


class StaffService:
    def __init__(self, gateway: DataGateway, principal: Principal | None) -> None:
        self._gw = gateway
        self._principal = principal

    def _actor(self) -> Principal:
        return require(self._principal, Permission.STAFF_MANAGE)

    async def _technicians(self) -> dict[str, Technician]:
        return {t.id: t for t in await self._gw.technicians.list()}

    async def _staff_user(self, user_id: str) -> UserAccount:
        user = await self._gw.auth.get_user(user_id)
        if user.role not in STAFF_ROLES:
            raise NotFoundError("Colaborador não encontrado.")
        return user

    async def _open_orders_of(self, technician_id: str | None) -> int:
        if not technician_id:
            return 0
        return sum(
            1 for o in await self._gw.orders.list() if o.technician_id == technician_id and o.status in OPEN_STATUSES
        )

    async def list_staff(self) -> list[StaffMember]:
        self._actor()
        technicians = await self._technicians()
        users = [u for u in await self._gw.auth.list_users() if u.role in STAFF_ROLES]
        users.sort(key=lambda u: (not u.active, u.name.casefold()))
        return [StaffMember(u, technicians.get(u.technician_id or "")) for u in users]

    async def create(self, form: Mapping[str, Any]) -> UserAccount:
        self._actor()
        name, email, specialty = _text(form, "name"), _text(form, "email").lower(), _text(form, "specialty")
        password = str(form.get("password", ""))
        if not name or not email:
            raise ValidationError("Preencha o nome e o e-mail do colaborador.")
        if not _EMAIL_RE.match(email):
            raise ValidationError("E-mail: informe um e-mail válido.")
        role = parse_staff_role(_text(form, "role"))
        if role == Role.TECHNICIAN and not specialty:
            raise ValidationError("Informe a especialidade do técnico.")
        check_password_policy(password)
        if await self._gw.auth.email_in_use(email):
            raise ValidationError(f"Já existe uma conta com o e-mail {email}.")
        if self._gw.remote_accounts:
            # Backend com contas remotas: o técnico é a própria conta, com a especialidade.
            return await self._gw.auth.create_user(name, email, role, password, specialty=specialty)
        technician_id = None
        if role == Role.TECHNICIAN:
            technician_id = (await self._gw.technicians.create(name, specialty)).id
        return await self._gw.auth.create_user(name, email, role, password, technician_id)

    async def update(self, user_id: str, form: Mapping[str, Any]) -> UserAccount:
        actor = self._actor()
        target = await self._staff_user(user_id)
        name, specialty = _text(form, "name"), _text(form, "specialty")
        if not name:
            raise ValidationError("Preencha o nome do colaborador.")
        role = parse_staff_role(_text(form, "role"))
        if role != Role.ADMIN:
            ensure_not_self(actor.user_id, user_id, "Não é possível retirar o próprio cargo de Administrador.")
        ensure_admin_remains(await self._gw.auth.list_users(), user_id, role, target.active)
        if self._gw.remote_accounts:
            return await self._update_remote(target, name, role, specialty)
        technicians = await self._technicians()
        technician_id = target.technician_id
        if target.role == Role.TECHNICIAN and role != Role.TECHNICIAN:
            ensure_technician_can_leave(await self._open_orders_of(technician_id))
            if technician_id in technicians:
                await self._gw.technicians.update(technicians[technician_id].model_copy(update={"active": False}))
        elif role == Role.TECHNICIAN:
            if not specialty:
                raise ValidationError("Informe a especialidade do técnico.")
            if technician_id in technicians:
                await self._gw.technicians.update(
                    technicians[technician_id].model_copy(
                        update={"name": name, "specialty": specialty, "active": target.active}
                    )
                )
            else:
                technician_id = (await self._gw.technicians.create(name, specialty)).id
        updated = target.model_copy(update={"name": name, "role": role, "technician_id": technician_id})
        return await self._gw.auth.update_user(updated)

    async def _update_remote(self, target: UserAccount, name: str, role: Role, specialty: str) -> UserAccount:
        """Contas remotas: perfil e especialidade ficam na própria conta do técnico."""
        if target.role == Role.TECHNICIAN and role != Role.TECHNICIAN:
            ensure_technician_can_leave(await self._open_orders_of(target.technician_id))
        if role == Role.TECHNICIAN and not specialty:
            raise ValidationError("Informe a especialidade do técnico.")
        updated = await self._gw.auth.update_user(target.model_copy(update={"name": name, "role": role}))
        if role == Role.TECHNICIAN:
            await self._gw.technicians.update(
                Technician(id=updated.id, name=name, specialty=specialty, active=updated.active)
            )
            updated = updated.model_copy(update={"technician_id": updated.id})
        return updated

    async def set_active(self, user_id: str, active: bool) -> UserAccount:
        actor = self._actor()
        target = await self._staff_user(user_id)
        if not active:
            ensure_not_self(actor.user_id, user_id, "Não é possível desativar a própria conta.")
            if target.role == Role.TECHNICIAN:
                ensure_technician_can_leave(await self._open_orders_of(target.technician_id))
        ensure_admin_remains(await self._gw.auth.list_users(), user_id, target.role, active)
        technicians = {} if self._gw.remote_accounts else await self._technicians()
        if target.role == Role.TECHNICIAN and target.technician_id in technicians:
            await self._gw.technicians.update(
                technicians[target.technician_id].model_copy(update={"active": active})
            )
        # A sessão de uma conta inativa é recusada em AuthService.resolve.
        return await self._gw.auth.update_user(target.model_copy(update={"active": active}))

    async def reset_password(self, user_id: str, password: str) -> UserAccount:
        self._actor()
        target = await self._staff_user(user_id)
        check_password_policy(password)
        return await self._gw.auth.update_user(target, new_password=password)
