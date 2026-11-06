"""Painel administrativo: indicadores e ordens recentes."""

from __future__ import annotations

import reflex as rx

from ..components import admin_shell, panel, panel_header, payment_badge, stat_card, status_badge, table
from ..state import AdminState


def _recent_row(order) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(order["code"], href="/admin/ordens/" + order["code"], class_name="code-link")),
        rx.table.cell(order["client"]),
        rx.table.cell(order["equipment"]),
        rx.table.cell(status_badge(order["status"], order["status_class"])),
        rx.table.cell(payment_badge(order["payment_status"], order["payment_class"])),
    )


def _status_bar(row) -> rx.Component:
    return rx.box(
        rx.flex(rx.text(row["status"]), rx.spacer(), rx.text(row["count"], class_name="bar-count")),
        rx.box(rx.box(class_name="bar-fill " + row["status_class"], width=row["percent"]), class_name="bar-track"),
        class_name="bar-row",
    )


def dashboard_page() -> rx.Component:
    m = AdminState.metrics
    return admin_shell(
        "Visão geral",
        "Acompanhe a operação da assistência em um só lugar.",
        rx.grid(
            stat_card(m["open"], "Ordens em aberto", "Do recebimento até a conclusão"),
            stat_card(m["awaiting"], "Aguardando aprovação", "Orçamentos enviados ao cliente"),
            stat_card(m["ready"], "Prontas para entrega", "Ordens concluídas"),
            stat_card(m["receivable"], "Valor a receber", "Saldo das ordens não canceladas"),
            columns="4",
            spacing="4",
            class_name="metrics-grid",
        ),
        rx.grid(
            panel(
                panel_header("Ordens recentes", rx.link("Ver todas →", href="/admin/ordens", class_name="accent-link")),
                table(["Código", "Cliente", "Equipamento", "Status", "Pagamento"], AdminState.recent_orders,
                      _recent_row, "Nenhuma ordem de serviço registrada."),
            ),
            panel(
                panel_header("Ordens por status"),
                rx.vstack(rx.foreach(AdminState.status_summary, _status_bar), spacing="3", width="100%"),
                rx.flex(
                    rx.text(m["clients"], " clientes"),
                    rx.text(m["equipment"], " equipamentos"),
                    rx.text(m["orders"], " ordens"),
                    gap="4",
                    wrap="wrap",
                    class_name="muted tiny summary-line",
                ),
            ),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
            class_name="dashboard-grid",
        ),
        rx.cond(
            AdminState.is_demo,
            rx.box(
                rx.text("Dados demonstrativos", class_name="demo-label"),
                rx.text("Os registros exibidos são fictícios e existem apenas enquanto a aplicação estiver em "
                        "execução.", class_name="muted tiny"),
                class_name="demo-notice",
            ),
        ),
    )
