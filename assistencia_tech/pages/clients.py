"""Páginas de clientes: lista com cadastro, edição e exclusão; detalhe com histórico."""

from __future__ import annotations

import reflex as rx

from ..components import (
    admin_shell,
    confirm_dialog,
    dialog_actions,
    empty_state,
    field,
    form_dialog,
    panel,
    panel_header,
    payment_badge,
    small_button,
    status_badge,
    submit_button,
    table,
    text_input,
)
from ..state import ClientDetailState, ClientState

CPF_HINT = "Com ou sem pontuação."
PHONE_HINT = "Com DDD. Ex.: (11) 98765-4321"


def _client_fields(values=None) -> rx.Component:
    def default(key: str):
        return {"default_value": values[key]} if values is not None else {}

    return rx.grid(
        field("Nome", text_input("name", "Nome completo", required=True, **default("name"))),
        field("CPF", text_input("cpf", "000.000.000-00", required=True, **default("cpf")), CPF_HINT),
        field("E-mail", text_input("email", "cliente@email.com", type="email", required=True, **default("email"))),
        field("Telefone", text_input("phone", "(11) 98765-4321", required=True, **default("phone")), PHONE_HINT),
        columns=rx.breakpoints(initial="1", md="2", xl="4"),
        spacing="3",
        width="100%",
    )


def _client_row(client) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(client["name"], href="/admin/clientes/" + client["id"], class_name="code-link")),
        rx.table.cell(client["cpf"]),
        rx.table.cell(client["email"]),
        rx.table.cell(client["phone"]),
        rx.table.cell(
            rx.flex(
                small_button("Editar", on_click=ClientState.open_edit(client)),
                small_button("Excluir", "danger", on_click=ClientState.ask_delete(client)),
                gap="2",
            )
        ),
    )


def clients_page() -> rx.Component:
    return admin_shell(
        "Clientes",
        "Cadastre, consulte e mantenha os dados dos clientes.",
        panel(
            rx.heading("Novo cliente", size="4"),
            rx.form(
                _client_fields(),
                submit_button("Adicionar cliente"),
                on_submit=ClientState.add_client,
                reset_on_submit=True,
                class_name="stack-form",
            ),
        ),
        panel(
            panel_header(
                "Lista de clientes",
                rx.input(value=ClientState.search, on_change=ClientState.set_search,
                         placeholder="Buscar por nome, e-mail, CPF ou telefone…", class_name="input search-input",
                         aria_label="Buscar clientes"),
            ),
            table(["Nome", "CPF", "E-mail", "Telefone", "Ações"], ClientState.filtered_clients, _client_row,
                  "Nenhum cliente encontrado."),
        ),
        form_dialog(
            "Editar cliente",
            "As mesmas validações do cadastro são aplicadas.",
            ClientState.edit_open,
            ClientState.set_edit_open,
            rx.form(_client_fields(ClientState.edit_values), dialog_actions("Salvar alterações"),
                    on_submit=ClientState.save_edit, class_name="stack-form"),
        ),
        confirm_dialog(
            "Excluir cliente",
            rx.text("Confirma a exclusão de ", rx.text.strong(ClientState.delete_name),
                    "? Clientes com equipamentos ou ordens não podem ser excluídos."),
            ClientState.delete_open,
            ClientState.set_delete_open,
            ClientState.confirm_delete,
            "Excluir",
        ),
    )


def _detail_equipment_row(equipment) -> rx.Component:
    return rx.table.row(
        rx.table.cell(equipment["description"]),
        rx.table.cell(equipment["serial_display"]),
        rx.table.cell(equipment["orders_count"]),
    )


def _detail_order_row(order) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(order["code"], href="/admin/ordens/" + order["code"], class_name="code-link")),
        rx.table.cell(order["opened_at"]),
        rx.table.cell(order["equipment"]),
        rx.table.cell(status_badge(order["status"], order["status_class"])),
        rx.table.cell(order["total"]),
        rx.table.cell(payment_badge(order["payment_status"], order["payment_class"])),
    )


def _info(label: str, value) -> rx.Component:
    return rx.box(rx.text(label, class_name="info-label"), rx.text(value, class_name="info-value"))


def client_detail_page() -> rx.Component:
    c = ClientDetailState.client
    return admin_shell(
        rx.cond(ClientDetailState.found, c["name"], "Cliente"),
        "Dados do cliente e histórico de atendimentos.",
        rx.cond(
            ClientDetailState.found,
            rx.vstack(
                panel(
                    rx.grid(_info("CPF", c["cpf"]), _info("E-mail", c["email"]), _info("Telefone", c["phone"]),
                            columns=rx.breakpoints(initial="1", md="3"), spacing="4", width="100%"),
                ),
                panel(
                    panel_header("Equipamentos"),
                    table(["Equipamento", "Número de série", "Ordens"], ClientDetailState.client_equipment,
                          _detail_equipment_row, "Nenhum equipamento cadastrado para este cliente."),
                ),
                panel(
                    panel_header("Histórico de atendimentos"),
                    table(["Código", "Abertura", "Equipamento", "Status", "Total", "Pagamento"],
                          ClientDetailState.client_orders, _detail_order_row,
                          "Nenhuma ordem de serviço para este cliente."),
                ),
                spacing="5",
                width="100%",
            ),
            rx.cond(
                ClientDetailState.data_error == "",
                panel(empty_state("Cliente não encontrado."),
                      rx.link("← Voltar à lista de clientes", href="/admin/clientes", class_name="accent-link")),
            ),
        ),
        back=("Clientes", "/admin/clientes"),
    )
