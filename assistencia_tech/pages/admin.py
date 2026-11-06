"""Páginas de colaboradores (Administrador) e relatórios (Administrador e Atendente)."""

from __future__ import annotations

import reflex as rx

from ..components import (
    admin_shell,
    confirm_dialog,
    dialog_actions,
    field,
    form_dialog,
    panel,
    panel_header,
    small_button,
    stat_card,
    submit_button,
    table,
    text_input,
    values_select,
)
from ..domain.staff_rules import STAFF_ROLE_VALUES
from ..state.admin import ReportsState, StaffState

ROLES = list(STAFF_ROLE_VALUES)
IN_PERIOD = "Entre as abertas no período"


# ------------------------------------------------------------- colaboradores
def _staff_row(member) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(member["name"], rx.cond(member["is_self"] == "1", " (você)", ""))),
        rx.table.cell(member["email"]),
        rx.table.cell(member["role"]),
        rx.table.cell(member["specialty_display"]),
        rx.table.cell(rx.text(member["status"], class_name=member["status_class"])),
        rx.table.cell(
            rx.flex(
                small_button("Editar", on_click=StaffState.open_edit(member)),
                small_button("Senha", on_click=StaffState.open_password(member)),
                rx.cond(
                    member["is_self"] == "1",
                    rx.fragment(),
                    rx.cond(
                        member["active"] == "1",
                        small_button("Desativar", "danger", on_click=StaffState.ask_toggle(member)),
                        small_button("Reativar", on_click=StaffState.ask_toggle(member)),
                    ),
                ),
                gap="2",
                wrap="wrap",
            )
        ),
    )


def _create_form() -> rx.Component:
    return rx.form(
        rx.grid(
            field("Nome", text_input("name", "Nome completo", required=True)),
            field("E-mail", text_input("email", "nome@assistencia.test", type="email", required=True)),
            field("Cargo", values_select("role", ROLES, "Cargo", value=StaffState.new_role,
                                         on_change=StaffState.set_new_role)),
            field("Especialidade", text_input("specialty", "Ex.: Impressoras",
                                              disabled=StaffState.new_role != "Técnico"),
                  "Obrigatória para técnicos."),
            field("Senha provisória", text_input("password", "Mín. 8 caracteres, letras e números",
                                                 type="password", required=True,
                                                 custom_attrs={"autocomplete": "new-password"})),
            columns=rx.breakpoints(initial="1", md="2", xl="5"),
            spacing="3",
            width="100%",
        ),
        submit_button("Cadastrar colaborador"),
        on_submit=StaffState.create,
        reset_on_submit=False,
        key=StaffState.form_key,
        class_name="stack-form",
    )


def staff_page() -> rx.Component:
    return admin_shell(
        "Colaboradores",
        "Gerencie as contas, os cargos e o acesso da equipe.",
        panel(rx.heading("Novo colaborador", size="4"), _create_form()),
        panel(
            panel_header("Equipe"),
            table(["Nome", "E-mail", "Cargo", "Especialidade", "Situação", "Ações"], StaffState.members,
                  _staff_row, "Nenhum colaborador cadastrado."),
            rx.text("Desativar revoga o acesso imediatamente. Técnicos inativos continuam no histórico das ordens.",
                    class_name="muted tiny"),
        ),
        form_dialog(
            "Editar colaborador",
            "Técnicos com ordens em aberto não podem mudar de cargo.",
            StaffState.edit_open,
            StaffState.set_edit_open,
            rx.form(
                field("Nome", text_input("name", "Nome", required=True, default_value=StaffState.edit_values["name"])),
                field("Cargo", values_select("role", ROLES, "Cargo", value=StaffState.edit_role,
                                             on_change=StaffState.set_edit_role)),
                field("Especialidade", text_input("specialty", "Ex.: Impressoras",
                                                  default_value=StaffState.edit_values["specialty"],
                                                  disabled=StaffState.edit_role != "Técnico")),
                dialog_actions("Salvar alterações"),
                on_submit=StaffState.save_edit,
                class_name="stack-form",
            ),
        ),
        form_dialog(
            "Redefinir senha provisória",
            rx.text("Nova senha para ", rx.text.strong(StaffState.toggle_name), ". A senha anterior deixa de valer."),
            StaffState.password_open,
            StaffState.set_password_open,
            rx.form(
                field("Nova senha provisória", text_input("password", "Mín. 8 caracteres, letras e números",
                                                          type="password", required=True,
                                                          custom_attrs={"autocomplete": "new-password"})),
                dialog_actions("Redefinir senha"),
                on_submit=StaffState.save_password,
                key=StaffState.password_key,
                class_name="stack-form",
            ),
        ),
        confirm_dialog(
            rx.cond(StaffState.toggle_activate, "Reativar colaborador", "Desativar colaborador"),
            rx.text(rx.cond(StaffState.toggle_activate, "Reativar o acesso de ", "Desativar o acesso de "),
                    rx.text.strong(StaffState.toggle_name), "?"),
            StaffState.toggle_open,
            StaffState.set_toggle_open,
            StaffState.confirm_toggle,
            "Confirmar",
        ),
    )


# ---------------------------------------------------------------- relatórios
def _method_row(row) -> rx.Component:
    return rx.table.row(rx.table.cell(row["method"]), rx.table.cell(row["amount"]))


def _technician_row(row) -> rx.Component:
    return rx.table.row(
        rx.table.cell(row["name"]),
        rx.table.cell(row["assigned"]),
        rx.table.cell(row["finished"]),
        rx.table.cell(row["budget"]),
    )


def reports_page() -> rx.Component:
    s = ReportsState.summary
    return admin_shell(
        "Relatórios",
        "Indicadores operacionais e financeiros por período.",
        panel(
            rx.form(
                rx.flex(
                    field("Data inicial", rx.input(name="start", type="date", default_value=ReportsState.start,
                                                   required=True, class_name="input")),
                    field("Data final", rx.input(name="end", type="date", default_value=ReportsState.end,
                                                 required=True, class_name="input")),
                    submit_button("Atualizar"),
                    rx.button("Exportar CSV", type="button", on_click=ReportsState.export_csv,
                              disabled=~ReportsState.loaded, class_name="btn btn-outline"),
                    gap="3",
                    align="end",
                    wrap="wrap",
                ),
                on_submit=ReportsState.apply_period,
                reset_on_submit=False,
                key=ReportsState.start + ReportsState.end,
            ),
            rx.text("Ordens consideradas pela data de abertura; recebimentos pela data do pagamento.",
                    class_name="muted tiny"),
        ),
        rx.grid(
            stat_card(s["opened"], "Ordens abertas", "No período"),
            stat_card(s["in_progress"], "Em andamento", IN_PERIOD),
            stat_card(s["delivered"], "Entregues", IN_PERIOD),
            stat_card(s["cancelled"], "Canceladas", IN_PERIOD),
            columns=rx.breakpoints(initial="2", lg="4"),
            spacing="3",
            class_name="metrics-grid",
        ),
        rx.grid(
            stat_card(s["received"], "Total recebido", "Pagamentos no período"),
            stat_card(s["ticket"], "Ticket médio", "Ordens entregues no período"),
            stat_card(s["turnaround"], "Tempo médio de reparo", "Da abertura à conclusão"),
            columns=rx.breakpoints(initial="1", md="3"),
            spacing="3",
            class_name="metrics-grid",
        ),
        rx.grid(
            panel(panel_header("Recebimentos por forma de pagamento"),
                  table(["Forma", "Valor"], ReportsState.methods, _method_row, "Sem recebimentos.")),
            panel(panel_header("Produção por técnico"),
                  table(["Técnico", "Atribuídas", "Concluídas", "Valor orçado"], ReportsState.technician_rows,
                        _technician_row, "Nenhuma ordem atribuída no período.")),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
        ),
    )
