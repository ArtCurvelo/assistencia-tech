"""Estados das páginas de colaboradores e relatórios."""

from __future__ import annotations

import reflex as rx

from ..data.errors import DataAccessError
from ..domain.permissions import Permission
from ..presenters import report_view, staff_row
from ..services import ReportService, StaffService
from .base import AppState


class StaffState(AppState):
    members: list[dict[str, str]] = []
    form_key: int = 0

    edit_open: bool = False
    edit_id: str = ""
    edit_values: dict[str, str] = {}
    edit_role: str = ""

    password_open: bool = False
    password_key: int = 0

    toggle_open: bool = False
    toggle_name: str = ""
    toggle_activate: bool = False

    new_role: str = "Atendente"

    async def _service(self) -> StaffService:
        return StaffService(self._gateway(), await self._current())

    async def _reload(self) -> None:
        principal = await self._current()
        members = await StaffService(self._gateway(), principal).list_staff()
        actor_id = principal.user_id if principal else ""
        self.members = [staff_row(m.user, m.technician, actor_id) for m in members]
        self.data_error = ""

    async def load_staff(self):
        self._clear_feedback()
        redirect = await self._guard(Permission.STAFF_MANAGE)
        if redirect is not None:
            return redirect
        try:
            await self._reload()
        except DataAccessError as error:
            self.data_error = error.user_message

    def set_new_role(self, value: str):
        self.new_role = value

    async def _run(self, action, message: str, after=None):
        if not self._start():
            return
        yield
        try:
            await action(await self._service())
            if after:
                after()
            await self._reload()
            yield self._succeed(message)
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    def _after_create(self):
        self.form_key += 1
        self.new_role = "Atendente"

    async def create(self, form_data: dict):
        form = {**form_data, "role": self.new_role}
        async for event in self._run(lambda s: s.create(form), f"Colaborador {form.get('name', '')} cadastrado.",
                                     self._after_create):
            yield event

    # -------------------------------------------------------------- edição
    def open_edit(self, member: dict):
        self._clear_feedback()
        self.edit_id = member["id"]
        self.edit_values = {"name": member["name"], "specialty": member["specialty"]}
        self.edit_role = member["role"]
        self.edit_open = True

    def set_edit_open(self, value: bool):
        self.edit_open = value

    def set_edit_role(self, value: str):
        self.edit_role = value

    def _close_edit(self):
        self.edit_open = False

    async def save_edit(self, form_data: dict):
        form = {**form_data, "role": self.edit_role}
        async for event in self._run(lambda s: s.update(self.edit_id, form), "Dados do colaborador atualizados.",
                                     self._close_edit):
            yield event

    # --------------------------------------------------------------- senha
    def open_password(self, member: dict):
        self._clear_feedback()
        self.edit_id = member["id"]
        self.toggle_name = member["name"]
        self.password_key += 1
        self.password_open = True

    def set_password_open(self, value: bool):
        self.password_open = value

    def _close_password(self):
        self.password_open = False

    async def save_password(self, form_data: dict):
        password = form_data.get("password", "")
        async for event in self._run(lambda s: s.reset_password(self.edit_id, password),
                                     f"Senha provisória de {self.toggle_name} redefinida.", self._close_password):
            yield event

    # ------------------------------------------------------------ ativação
    def ask_toggle(self, member: dict):
        self._clear_feedback()
        self.edit_id = member["id"]
        self.toggle_name = member["name"]
        self.toggle_activate = member["active"] != "1"
        self.toggle_open = True

    def set_toggle_open(self, value: bool):
        self.toggle_open = value

    def _close_toggle(self):
        self.toggle_open = False

    async def confirm_toggle(self):
        activate = self.toggle_activate
        label = "reativado" if activate else "desativado"
        async for event in self._run(lambda s: s.set_active(self.edit_id, activate),
                                     f"Colaborador {self.toggle_name} {label}.", self._close_toggle):
            yield event
        self.toggle_open = False


class ReportsState(AppState):
    start: str = ""
    end: str = ""
    summary: dict[str, str] = {}
    methods: list[dict[str, str]] = []
    technician_rows: list[dict[str, str]] = []
    satisfaction: dict[str, str] = {}
    comments: list[dict[str, str]] = []
    loaded: bool = False

    async def _build(self, start: str, end: str) -> None:
        service = ReportService(self._gateway(), await self._current())
        period = service.period(start, end)
        view = report_view(await service.report(period))
        self.start, self.end = period.start.isoformat(), period.end.isoformat()
        self.summary = view["summary"]
        self.methods = view["methods"]
        self.technician_rows = view["technicians"]
        self.satisfaction = view["satisfaction"]
        self.comments = view["comments"]
        self.loaded = True
        self.data_error = ""

    async def load_reports(self):
        self._clear_feedback()
        redirect = await self._guard(Permission.REPORTS_VIEW)
        if redirect is not None:
            return redirect
        try:
            period = ReportService(self._gateway(), await self._current()).default_period()
            await self._build(period.start.isoformat(), period.end.isoformat())
        except DataAccessError as error:
            self.data_error = error.user_message

    async def apply_period(self, form_data: dict):
        if not self._start():
            return
        yield
        try:
            await self._build(form_data.get("start", ""), form_data.get("end", ""))
            yield self._succeed("Relatório atualizado.")
        except DataAccessError as error:
            yield self._fail(error)
        finally:
            self.is_loading = False

    async def export_csv(self):
        try:
            service = ReportService(self._gateway(), await self._current())
            filename, content = await service.export_csv(service.period(self.start, self.end))
        except DataAccessError as error:
            yield self._fail(error)
            return
        yield rx.download(data=content, filename=filename, mime_type="text/csv;charset=utf-8")
