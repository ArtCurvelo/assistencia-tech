"""Portal do cliente: dados da conta, lista e detalhe das próprias ordens."""

from __future__ import annotations

import reflex as rx

from ..components import (
    button,
    data_error_alert,
    dialog_actions,
    field,
    form_dialog,
    empty_state,
    panel,
    panel_header,
    payment_badge,
    public_page,
    status_badge,
    table,
)
from ..state import PortalOrderState, PortalState


def _info(label: str, value) -> rx.Component:
    return rx.box(rx.text(label, class_name="info-label"), rx.text(value, class_name="info-value"))


def _portal_shell(title, subtitle, *children) -> rx.Component:
    return public_page(
        rx.box(
            rx.text("MINHA CONTA", class_name="eyebrow"),
            rx.heading(title, size="8"),
            rx.text(subtitle, class_name="muted"),
            class_name="page-header page-width",
        ),
        rx.vstack(data_error_alert(), *children, spacing="5", class_name="page-width portal-content"),
    )


def _order_row(order) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.link(order["code"], href="/minha-conta/ordens/" + order["code"], class_name="code-link")),
        rx.table.cell(order["equipment"]),
        rx.table.cell(status_badge(order["status"], order["status_class"])),
        rx.table.cell(rx.cond(order["warranty_until"] != "", rx.text("Garantia até ", order["warranty_until"]),
                              order["due_date"])),
        rx.table.cell(order["updated_at"]),
        rx.table.cell(order["total"]),
        rx.table.cell(order["balance"]),
        rx.table.cell(payment_badge(order["payment_status"], order["payment_class"])),
    )


def portal_page() -> rx.Component:
    a = PortalState.account
    return _portal_shell(
        rx.text("Olá, ", PortalState.user_name),
        "Acompanhe seus equipamentos e ordens de serviço.",
        panel(
            rx.grid(_info("E-mail", a["email"]), _info("CPF", a["cpf"]), _info("Telefone", a["phone"]),
                    columns=rx.breakpoints(initial="1", md="3"), spacing="4", width="100%"),
        ),
        panel(
            panel_header("Minhas ordens de serviço"),
            rx.cond(
                PortalState.my_orders.length() > 0,
                table(["Código", "Equipamento", "Status", "Previsão / garantia", "Atualização", "Total", "Saldo", "Pagamento"],
                      PortalState.my_orders, _order_row, "Nenhuma ordem de serviço."),
                rx.box(
                    empty_state("Você ainda não possui ordens de serviço."),
                    rx.text("Para solicitar um atendimento, leve o equipamento à assistência; a ordem aparecerá "
                            "aqui assim que for aberta.", class_name="muted tiny"),
                    rx.link("Conheça nossos serviços →", href="/servicos", class_name="accent-link"),
                ),
            ),
        ),
    )


def _item_row(item) -> rx.Component:
    return rx.table.row(
        rx.table.cell(item["kind"]),
        rx.table.cell(item["description"]),
        rx.table.cell(item["quantity"]),
        rx.table.cell(item["unit_price"]),
        rx.table.cell(item["subtotal"]),
    )


def _payment_row(payment) -> rx.Component:
    return rx.table.row(rx.table.cell(payment["paid_at"]), rx.table.cell(payment["method"]),
                        rx.table.cell(payment["amount"]))


def _event(event) -> rx.Component:
    return rx.box(
        rx.box(class_name="timeline-dot"),
        rx.box(rx.text(event["at"], class_name="muted tiny"), rx.text(event["description"]),
               class_name="timeline-body"),
        class_name="timeline-item",
    )


def _decision_panel() -> rx.Component:
    t = PortalOrderState.totals
    return rx.cond(
        PortalOrderState.can_decide,
        panel(
            panel_header("Orçamento aguardando a sua aprovação"),
            rx.text("Confira os itens abaixo. Ao aprovar, o reparo é iniciado; ao recusar, a ordem é cancelada "
                    "e o equipamento fica disponível para retirada.", class_name="muted"),
            rx.text("Total do orçamento: ", rx.el.strong(t["total"])),
            rx.flex(
                button("Aprovar orçamento", on_click=PortalOrderState.approve_budget,
                       loading=PortalOrderState.is_loading, disabled=PortalOrderState.is_loading),
                button("Recusar orçamento", outline=True, on_click=PortalOrderState.set_refuse_open(True),
                       disabled=PortalOrderState.is_loading),
                gap="3",
                wrap="wrap",
            ),
            class_name="decision-panel",
        ),
    )


def _score_button(score: str) -> rx.Component:
    chosen = PortalOrderState.rate_score == score
    return rx.button(
        score,
        type="button",
        on_click=PortalOrderState.choose_score(score),
        class_name=rx.cond(chosen, "score-btn score-btn-active", "score-btn"),
        aria_pressed=rx.cond(chosen, "true", "false"),
        aria_label="Nota " + score,
    )


def _rating_panel() -> rx.Component:
    """Avaliação do atendimento após a entrega (add-service-rating)."""
    r = PortalOrderState.rating
    return rx.cond(
        PortalOrderState.can_rate,
        panel(
            panel_header("Avalie o atendimento"),
            rx.text(PortalOrderState.rating_question),
            rx.form(
                rx.flex(*[_score_button(str(n)) for n in range(11)], gap="2", wrap="wrap", role="group",
                        aria_label="Nota de 0 a 10"),
                rx.flex(rx.text("0 = nada provável", class_name="muted tiny"),
                        rx.text("10 = com certeza", class_name="muted tiny"), justify="between"),
                field("Comentário (opcional)", rx.text_area(name="comment", max_length=500, class_name="input",
                                                           placeholder="Conte como foi o atendimento")),
                rx.button("Enviar avaliação", type="submit", loading=PortalOrderState.is_loading,
                          disabled=(PortalOrderState.rate_score == "") | PortalOrderState.is_loading,
                          class_name="btn btn-primary"),
                rx.text("A avaliação é enviada uma única vez e não pode ser alterada.", class_name="muted tiny"),
                on_submit=PortalOrderState.submit_rating,
                class_name="stack-form",
            ),
            class_name="decision-panel",
        ),
        rx.cond(
            r["score"] != "",
            panel(
                panel_header("Sua avaliação"),
                rx.flex(rx.text(r["score"], class_name="rating-score"), rx.text("de 10", class_name="muted"),
                        rx.text("Avaliada em ", r["at"], class_name="muted tiny"), gap="12px", align="center",
                        wrap="wrap"),
                rx.cond(r["comment"] != "", rx.text("\u201c", r["comment"], "\u201d", class_name="rating-comment")),
            ),
        ),
    )


def _refuse_dialog() -> rx.Component:
    return form_dialog(
        "Recusar orçamento",
        "Conte o motivo da recusa. A ordem será cancelada e o motivo fica registrado.",
        PortalOrderState.refuse_open,
        PortalOrderState.set_refuse_open,
        rx.form(
            field("Motivo da recusa", rx.text_area(name="reason", class_name="input",
                                                   placeholder="Ex.: o valor ficou acima do esperado")),
            dialog_actions("Confirmar recusa"),
            on_submit=PortalOrderState.confirm_refusal,
            class_name="stack-form",
        ),
    )


def portal_order_page() -> rx.Component:
    o, t = PortalOrderState.order, PortalOrderState.totals
    return _portal_shell(
        rx.cond(PortalOrderState.found, o["code"], "Ordem de serviço"),
        "Detalhes do seu atendimento.",
        rx.link("← Minhas ordens", href="/minha-conta", class_name="back-link"),
        rx.cond(
            PortalOrderState.found,
            rx.vstack(
                panel(
                    rx.flex(status_badge(o["status"], o["status_class"]),
                            payment_badge(o["payment_status"], o["payment_class"]),
                            rx.link("🧾 Comprovante (imprimir / PDF)",
                                    href="/minha-conta/ordens/" + o["code"] + "/comprovante",
                                    class_name="accent-link"),
                            gap="3", align="center", wrap="wrap"),
                    rx.grid(_info("Equipamento", o["equipment"]), _info("Problema relatado", o["problem"]),
                            _info("Última atualização", o["updated_at"]),
                            _info("Previsão de entrega", o["due_date"]),
                            rx.cond(o["warranty_until"] != "", _info("Garantia até", o["warranty_until"])),
                            rx.cond(o["warranty_of"] != "", _info("Atendimento em garantia da", o["warranty_of"])),
                            columns=rx.breakpoints(initial="1", md="3"), spacing="4", width="100%"),
                    rx.cond(o["diagnosis"] != "", rx.box(_info("Diagnóstico", o["diagnosis"]))),
                ),
                _decision_panel(),
                _rating_panel(),
                _refuse_dialog(),
                panel(
                    panel_header("Orçamento"),
                    table(["Tipo", "Descrição", "Qtd.", "Valor unitário", "Subtotal"], PortalOrderState.items,
                          _item_row, "O orçamento ainda não foi elaborado."),
                    rx.grid(_info("Total", t["total"]), _info("Pago", t["paid"]), _info("Saldo", t["balance"]),
                            columns="3", spacing="4", width="100%", class_name="totals-grid"),
                ),
                panel(panel_header("Pagamentos"),
                      table(["Data", "Forma", "Valor"], PortalOrderState.payments, _payment_row,
                            "Nenhum pagamento registrado.")),
                panel(panel_header("Andamento"),
                      rx.box(rx.foreach(PortalOrderState.timeline, _event), class_name="timeline")),
                spacing="5",
                width="100%",
            ),
            rx.cond(
                PortalOrderState.data_error == "",
                panel(empty_state("Ordem de serviço não encontrada."),
                      rx.link(button("Voltar às minhas ordens"), href="/minha-conta")),
            ),
        ),
    )
