"""Página de estoque: catálogo de peças, entrada de estoque e movimentações (add-parts-inventory)."""

from __future__ import annotations

import reflex as rx

from ..components import (
    admin_shell,
    dialog_actions,
    field,
    form_dialog,
    options_select,
    panel,
    panel_header,
    small_button,
    submit_button,
    table,
    text_input,
)
from ..state.inventory import InventoryState as S

ACTIVE_OPTIONS = [{"value": "sim", "label": "Ativa"}, {"value": "nao", "label": "Inativa"}]


def _part_fields(values=None) -> rx.Component:
    def default(key: str):
        return {"default_value": values[key]} if values is not None else {}

    fields = [
        field("Código", text_input("code", "Ex.: SSD-480", required=True, **default("code")), "Único no catálogo."),
        field("Nome", text_input("name", "Ex.: SSD 480 GB", required=True, **default("name"))),
        field("Preço de venda (R$)", text_input("unit_price", "Ex.: 250,00", required=True, **default("unit_price"))),
        field("Estoque mínimo", text_input("min_quantity", "0", **({"default_value": "0"} | default("min_quantity"))),
              "Abaixo disso a peça aparece como estoque baixo."),
    ]
    if values is not None:
        fields.append(field("Situação", options_select("active", ACTIVE_OPTIONS, "Situação", **default("active"))))
    return rx.grid(*fields, columns=rx.breakpoints(initial="1", md="2", xl="4"), spacing="3", width="100%")


def _part_row(part) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(part["code"], class_name="code-text")),
        rx.table.cell(part["name"]),
        rx.table.cell(part["price"]),
        rx.table.cell(rx.text(part["quantity"], class_name="qty-text")),
        rx.table.cell(part["min_quantity"]),
        rx.table.cell(rx.text(part["level"], class_name=part["level_class"])),
        rx.table.cell(
            rx.cond(
                S.can_manage_stock,
                rx.flex(
                    small_button("Entrada", on_click=S.open_restock(part)),
                    small_button("Editar", on_click=S.open_edit(part)),
                    gap="2",
                ),
                rx.text("—", class_name="muted"),
            )
        ),
    )


def _movement_row(move) -> rx.Component:
    return rx.table.row(
        rx.table.cell(move["at"]),
        rx.table.cell(move["part"]),
        rx.table.cell(rx.text(move["kind"], class_name=move["kind_class"])),
        rx.table.cell(rx.text(move["quantity"], class_name="qty-text")),
        rx.table.cell(rx.cond(move["order"] != "",
                              rx.link(move["order"], href="/admin/ordens/" + move["order"], class_name="code-link"),
                              rx.text("—", class_name="muted"))),
        rx.table.cell(move["author"]),
        rx.table.cell(move["note"]),
    )


def inventory_page() -> rx.Component:
    return admin_shell(
        "Estoque",
        "Catálogo de peças, reposição e movimentações. Peças usadas nos orçamentos saem do estoque automaticamente.",
        rx.cond(
            S.low_stock_count > 0,
            rx.box(
                rx.text(S.low_stock_count, " peça(s) com estoque baixo ou esgotado. Registre a entrada ao repor."),
                class_name="notice notice-warning",
            ),
        ),
        rx.cond(
            S.can_manage_stock,
            panel(
                rx.heading("Cadastrar peça", size="4"),
                rx.form(_part_fields(), submit_button("Adicionar peça"), on_submit=S.add_part,
                        reset_on_submit=False, key=S.form_key, class_name="stack-form"),
                rx.text("A peça começa com quantidade zero; use “Entrada” para registrar as unidades recebidas.",
                        class_name="muted tiny"),
            ),
        ),
        panel(
            panel_header(
                "Peças",
                rx.input(value=S.search, on_change=S.set_search, placeholder="Buscar código ou nome…",
                         class_name="input search-input", aria_label="Buscar peças"),
            ),
            table(["Código", "Nome", "Preço", "Qtd.", "Mínimo", "Situação", "Ações"], S.filtered_parts, _part_row,
                  "Nenhuma peça cadastrada."),
        ),
        panel(
            panel_header("Movimentações recentes"),
            table(["Data", "Peça", "Tipo", "Qtd.", "Ordem", "Autor", "Observação"], S.movements, _movement_row,
                  "Nenhuma movimentação registrada."),
        ),
        form_dialog(
            "Editar peça",
            "A quantidade não é editada aqui: ela muda pelas entradas e pelos orçamentos.",
            S.edit_open,
            S.set_edit_open,
            rx.form(_part_fields(S.edit_values), dialog_actions("Salvar alterações"), on_submit=S.save_edit,
                    class_name="stack-form"),
        ),
        form_dialog(
            "Entrada de estoque",
            rx.text("Peça: ", rx.text.strong(S.restock_name)),
            S.restock_open,
            S.set_restock_open,
            rx.form(
                rx.grid(
                    field("Quantidade recebida", text_input("quantity", "Ex.: 5", required=True)),
                    field("Observação", text_input("note", "Ex.: NF 1234, fornecedor")),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="3",
                    width="100%",
                ),
                dialog_actions("Registrar entrada"),
                on_submit=S.confirm_restock,
                class_name="stack-form",
            ),
        ),
    )
