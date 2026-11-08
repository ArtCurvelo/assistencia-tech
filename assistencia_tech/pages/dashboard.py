"""Painel administrativo: indicadores, gráficos e ordens recentes."""

from __future__ import annotations

import reflex as rx

from ..components import admin_shell, panel, panel_header, payment_badge, stat_card, status_badge, table
from ..presenters import PAYMENT_COLORS, STATUS_COLORS
from ..state import AdminState

AXIS_TICK = {"fill": "#a5b5c9", "fontSize": 12}
TOOLTIP_STYLE = {"backgroundColor": "#081a2f", "border": "1px solid #285071", "borderRadius": "8px"}


def _recent_row(order) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(order["code"], href="/admin/ordens/" + order["code"], class_name="code-link")),
        rx.table.cell(order["client"]),
        rx.table.cell(order["equipment"]),
        rx.table.cell(status_badge(order["status"], order["status_class"])),
        rx.table.cell(payment_badge(order["payment_status"], order["payment_class"])),
    )


def _status_chart() -> rx.Component:
    # As 7 situações vêm sempre na mesma ordem, então as cores são fixas por posição.
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#193653", horizontal=False),
        rx.recharts.x_axis(type_="number", allow_decimals=False, tick=AXIS_TICK, stroke="#285071"),
        rx.recharts.y_axis(data_key="status", type_="category", width=150, tick=AXIS_TICK, stroke="#285071"),
        rx.recharts.graphing_tooltip(content_style=TOOLTIP_STYLE, cursor={"fill": "rgba(8,124,255,0.08)"}),
        rx.recharts.bar(
            *[rx.recharts.cell(fill=color) for color in STATUS_COLORS.values()],
            data_key="quantidade",
            name="Ordens",
            radius=[0, 6, 6, 0],
            bar_size=16,
        ),
        data=AdminState.status_data,
        layout="vertical",
        width="100%",
        height=280,
        margin={"left": 0, "right": 16, "top": 4, "bottom": 4},
    )


def _payment_chart() -> rx.Component:
    return rx.box(
        rx.recharts.pie_chart(
            rx.recharts.graphing_tooltip(content_style=TOOLTIP_STYLE),
            rx.recharts.pie(
                *[rx.recharts.cell(fill=color) for color in PAYMENT_COLORS.values()],
                data=AdminState.payment_data,
                data_key="quantidade",
                name_key="situacao",
                inner_radius="55%",
                outer_radius="85%",
                padding_angle=3,
                stroke="#081a2f",
            ),
            width="100%",
            height=220,
        ),
        rx.box(
            *[
                rx.text(rx.el.span(class_name="legend-dot", style={"background": color}), name)
                for name, color in PAYMENT_COLORS.items()
            ],
            class_name="chart-legend",
        ),
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
            stat_card(m["nps"], "NPS (90 dias)", rx.fragment(m["nps_count"], " avaliação(ões) de clientes")),
            columns=rx.breakpoints(initial="2", lg="5"),
            spacing="3",
            class_name="metrics-grid",
        ),
        rx.cond(
            (m["overdue"] != "0") & (m["overdue"] != "—"),
            rx.link(
                rx.text("⏰ ", m["overdue"], " ordem(ns) atrasada(s): previsão de entrega vencida. Ver ordens →"),
                href="/admin/ordens",
                class_name="notice notice-error stock-alert",
            ),
        ),
        rx.cond(
            AdminState.low_stock_count > 0,
            rx.link(
                rx.text("⚠ ", AdminState.low_stock_count,
                        " peça(s) com estoque baixo ou esgotado. Ver estoque →"),
                href="/admin/estoque",
                class_name="notice notice-warning stock-alert",
            ),
        ),
        rx.grid(
            panel(
                panel_header("Ordens por status"),
                _status_chart(),
                rx.text(m["clients"], " clientes · ", m["equipment"], " equipamentos · ", m["orders"], " ordens",
                        class_name="muted tiny summary-line"),
            ),
            panel(
                panel_header("Situação dos pagamentos"),
                _payment_chart(),
                rx.text("Ordens com valor no orçamento, exceto as canceladas.", class_name="muted tiny"),
            ),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
            class_name="dashboard-grid",
        ),
        panel(
            panel_header("Ordens recentes", rx.link("Ver todas →", href="/admin/ordens", class_name="accent-link")),
            table(["Código", "Cliente", "Equipamento", "Status", "Pagamento"], AdminState.recent_orders,
                  _recent_row, "Nenhuma ordem de serviço registrada."),
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
