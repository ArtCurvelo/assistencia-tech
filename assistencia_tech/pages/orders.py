"""Lista e abertura de ordens de serviço."""

from __future__ import annotations

import reflex as rx

from ..components import (
    admin_shell,
    field,
    options_select,
    panel,
    panel_header,
    payment_badge,
    status_badge,
    submit_button,
    table,
)
from ..models import ORDER_STATUSES
from ..state import OrderState
from ..state.orders import ALL


def _row(order) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(order["code"], href="/admin/ordens/" + order["code"], class_name="code-link")),
        rx.table.cell(order["client"]),
        rx.table.cell(order["equipment"]),
        rx.table.cell(order["technician"]),
        rx.table.cell(status_badge(order["status"], order["status_class"])),
        rx.table.cell(order["total"]),
        rx.table.cell(payment_badge(order["payment_status"], order["payment_class"])),
    )


def _open_form() -> rx.Component:
    return rx.form(
        rx.grid(
            field("Cliente", options_select("client_id", OrderState.client_options, "Selecione o cliente",
                                            value=OrderState.new_client_id, on_change=OrderState.set_new_client)),
            field(
                "Equipamento",
                options_select("equipment_id", OrderState.equipment_options,
                               rx.cond(OrderState.new_client_id == "", "Escolha o cliente primeiro",
                                       "Selecione o equipamento"),
                               value=OrderState.new_equipment_id, on_change=OrderState.set_new_equipment,
                               disabled=OrderState.new_client_id == ""),
                "Somente equipamentos do cliente selecionado.",
            ),
            field("Problema relatado", rx.input(name="problem", placeholder="Descreva o defeito informado",
                                                required=True, class_name="input")),
            columns=rx.breakpoints(initial="1", md="3"),
            spacing="3",
            width="100%",
        ),
        rx.flex(
            submit_button("Abrir ordem"),
            rx.link("Equipamento não cadastrado? Cadastre aqui →", href="/admin/equipamentos",
                    class_name="accent-link tiny"),
            align="center",
            gap="4",
            wrap="wrap",
        ),
        on_submit=OrderState.open_order,
        reset_on_submit=False,
        key=OrderState.form_key,
        class_name="stack-form",
    )


def orders_page() -> rx.Component:
    status_options = [{"value": ALL, "label": "Todos os status"}] + [{"value": s, "label": s} for s in ORDER_STATUSES]
    return admin_shell(
        "Ordens de serviço",
        "Abra ordens, acompanhe o andamento e acesse o detalhe de cada atendimento.",
        rx.cond(OrderState.can_open_orders, panel(rx.heading("Abrir ordem de serviço", size="4"), _open_form())),
        panel(
            panel_header(
                "Ordens registradas",
                options_select("status_filter", status_options, "Status", value=OrderState.status_filter,
                               on_change=OrderState.set_status_filter),
                rx.select.root(
                    rx.select.trigger(placeholder="Técnico", class_name="input select-trigger"),
                    rx.select.content(
                        rx.select.item("Todos os técnicos", value=ALL),
                        rx.foreach(OrderState.technicians, lambda t: rx.select.item(t["label"], value=t["value"])),
                    ),
                    value=OrderState.technician_filter,
                    on_change=OrderState.set_technician_filter,
                ),
                rx.input(value=OrderState.search, on_change=OrderState.set_search,
                         placeholder="Buscar código, cliente ou equipamento…", class_name="input search-input",
                         aria_label="Buscar ordens"),
            ),
            table(["Código", "Cliente", "Equipamento", "Técnico", "Status", "Total", "Pagamento"],
                  OrderState.filtered_orders, _row, "Nenhuma ordem encontrada."),
        ),
        rx.text("Fluxo: Recebido → Em análise → Aguardando aprovação → Em reparo → Concluído → Entregue. "
                "O cancelamento é possível até o reparo.", class_name="muted tiny"),
    )
