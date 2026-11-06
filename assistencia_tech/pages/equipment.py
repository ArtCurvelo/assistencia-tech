"""Página de equipamentos: cadastro, filtros, edição, exclusão e histórico."""

from __future__ import annotations

import reflex as rx

from ..components import (
    admin_shell,
    confirm_dialog,
    dialog_actions,
    field,
    form_dialog,
    options_select,
    panel,
    panel_header,
    small_button,
    status_badge,
    submit_button,
    table,
    text_input,
    values_select,
)
from ..models import EQUIPMENT_KINDS
from ..state import EquipmentState
from ..state.equipment import ALL_KINDS


def _equipment_fields(values=None) -> rx.Component:
    def default(key: str):
        return {"default_value": values[key]} if values is not None else {}

    return rx.grid(
        field("Cliente", options_select("client_id", EquipmentState.client_options, "Selecione o cliente",
                                        required=True, **default("client_id"))),
        field("Tipo", values_select("kind", list(EQUIPMENT_KINDS), "Tipo de aparelho", required=True,
                                    **default("kind"))),
        field("Marca", text_input("brand", "Ex.: Lenovo", required=True, **default("brand"))),
        field("Modelo", text_input("model", "Ex.: IdeaPad 3", required=True, **default("model"))),
        field("Número de série", text_input("serial_number", "Opcional", **default("serial_number")),
              "Opcional, mas único quando informado."),
        field("Observações", text_input("notes", "Acessórios, estado de entrega…", **default("notes"))),
        columns=rx.breakpoints(initial="1", md="2", xl="3"),
        spacing="3",
        width="100%",
    )


def _row(equipment) -> rx.Component:
    return rx.table.row(
        rx.table.cell(equipment["client"]),
        rx.table.cell(equipment["kind"]),
        rx.table.cell(rx.text(equipment["brand"], " ", equipment["model"])),
        rx.table.cell(equipment["serial_display"]),
        rx.table.cell(equipment["orders_count"]),
        rx.table.cell(
            rx.flex(
                small_button("Histórico", on_click=EquipmentState.open_history(equipment)),
                small_button("Editar", on_click=EquipmentState.open_edit(equipment)),
                small_button("Excluir", "danger", on_click=EquipmentState.ask_delete(equipment)),
                gap="2",
            )
        ),
    )


def _history_row(order) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(order["code"], href="/admin/ordens/" + order["code"], class_name="code-link")),
        rx.table.cell(order["opened_at"]),
        rx.table.cell(order["problem"]),
        rx.table.cell(status_badge(order["status"], order["status_class"])),
    )


def equipment_page() -> rx.Component:
    return admin_shell(
        "Equipamentos",
        "Registre os aparelhos recebidos e consulte o histórico de manutenção.",
        panel(
            rx.heading("Cadastrar equipamento", size="4"),
            rx.form(_equipment_fields(), submit_button("Adicionar equipamento"),
                    on_submit=EquipmentState.add_equipment, reset_on_submit=True, class_name="stack-form"),
        ),
        panel(
            panel_header(
                "Equipamentos cadastrados",
                options_select("kind_filter", [{"value": ALL_KINDS, "label": "Todos os tipos"}]
                               + [{"value": k, "label": k} for k in EQUIPMENT_KINDS], "Tipo",
                               value=EquipmentState.kind_filter, on_change=EquipmentState.set_kind_filter),
                rx.input(value=EquipmentState.search, on_change=EquipmentState.set_search,
                         placeholder="Buscar cliente, marca, modelo ou série…", class_name="input search-input",
                         aria_label="Buscar equipamentos"),
            ),
            table(["Cliente", "Tipo", "Marca/modelo", "Nº de série", "Ordens", "Ações"],
                  EquipmentState.filtered_equipment, _row, "Nenhum equipamento encontrado."),
        ),
        form_dialog(
            "Editar equipamento",
            "O cliente só pode ser alterado se o equipamento não tiver ordens de serviço.",
            EquipmentState.edit_open,
            EquipmentState.set_edit_open,
            rx.form(_equipment_fields(EquipmentState.edit_values), dialog_actions("Salvar alterações"),
                    on_submit=EquipmentState.save_edit, class_name="stack-form"),
        ),
        confirm_dialog(
            "Excluir equipamento",
            rx.text("Confirma a exclusão de ", rx.text.strong(EquipmentState.delete_name),
                    "? Equipamentos com ordens de serviço não podem ser excluídos."),
            EquipmentState.delete_open,
            EquipmentState.set_delete_open,
            EquipmentState.confirm_delete,
            "Excluir",
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Histórico de manutenção"),
                rx.dialog.description(EquipmentState.history_title, class_name="muted"),
                table(["Código", "Abertura", "Problema", "Status"], EquipmentState.history_orders, _history_row,
                      "Nenhuma ordem de serviço para este equipamento."),
                rx.flex(rx.dialog.close(rx.button("Fechar", class_name="btn btn-outline")), justify="end",
                        class_name="dialog-actions"),
                class_name="dialog-card dialog-wide",
            ),
            open=EquipmentState.history_open,
            on_open_change=EquipmentState.set_history_open,
        ),
    )
