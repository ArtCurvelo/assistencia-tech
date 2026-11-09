"""Detalhe da ordem de serviço: técnico, diagnóstico, orçamento, pagamentos, status e histórico."""

from __future__ import annotations

import reflex as rx

from ..components import (
    admin_shell,
    dialog_actions,
    empty_state,
    field,
    form_dialog,
    options_select,
    panel,
    panel_header,
    payment_badge,
    small_button,
    status_badge,
    submit_button,
    table,
    text_input,
    values_select,
)
from ..models import PAYMENT_METHODS
from ..state import OrderDetailState as S

CANCELLED = "Cancelado"


def _info(label: str, value) -> rx.Component:
    return rx.box(rx.text(label, class_name="info-label"), rx.text(value, class_name="info-value"))


def _summary() -> rx.Component:
    o = S.order
    return panel(
        rx.flex(
            status_badge(o["status"], o["status_class"]),
            payment_badge(o["payment_status"], o["payment_class"]),
            rx.spacer(),
            rx.text("Aberta em ", o["opened_at"], " · atualizada em ", o["updated_at"], class_name="muted tiny"),
            align="center",
            gap="12px",
            wrap="wrap",
        ),
        rx.grid(
            _info("Cliente", rx.link(o["client"], href="/admin/clientes/" + o["client_id"], class_name="code-link")),
            _info("Equipamento", o["equipment"]),
            _info("Problema relatado", o["problem"]),
            columns=rx.breakpoints(initial="1", md="3"),
            spacing="4",
            width="100%",
        ),
        rx.cond(S.cancel_reason != "", rx.text("Motivo do cancelamento: ", S.cancel_reason, class_name="notice-error")),
        _deadlines(),
    )


def _deadlines() -> rx.Component:
    """Previsão, atraso e garantia (add-deadlines-and-warranty)."""
    o = S.order
    return rx.box(
        rx.grid(
            _info("Previsão de entrega", rx.flex(
                rx.text(o["due_date"]),
                rx.cond(o["late"] != "", rx.text(o["late"], class_name="late-badge")),
                gap="8px", align="center", wrap="wrap",
            )),
            rx.cond(o["warranty_until"] != "", _info("Garantia até", o["warranty_until"])),
            rx.cond(o["warranty_of"] != "", _info("Ordem em garantia da", rx.link(
                o["warranty_of"], href="/admin/ordens/" + o["warranty_of"], class_name="code-link"))),
            columns=rx.breakpoints(initial="1", md="3"),
            spacing="4",
            width="100%",
        ),
        rx.cond(
            S.permissions["due_editable"] == "1",
            rx.form(
                rx.flex(
                    rx.input(type="date", name="due_date", default_value=o["due_input"], key=o["due_input"],
                             class_name="input date-input", aria_label="Nova previsão de entrega"),
                    rx.button("Alterar previsão", type="submit", loading=S.is_loading, class_name="btn-sm btn-sm-ghost"),
                    gap="8px", align="center", wrap="wrap",
                ),
                on_submit=S.save_due_date,
                reset_on_submit=False,
            ),
        ),
        rx.cond(
            S.permissions["warranty_openable"] == "1",
            rx.button("Abrir ordem em garantia", on_click=S.set_warranty_open(True), class_name="btn btn-outline"),
        ),
        class_name="deadline-box",
    )


def _warranty_dialog() -> rx.Component:
    return form_dialog(
        "Abrir ordem em garantia",
        "Mesmo cliente e equipamento desta ordem. O atendimento em garantia não gera cobrança.",
        S.warranty_open,
        S.set_warranty_open,
        rx.form(
            field("Problema relatado", rx.text_area(name="problem", class_name="input", required=True,
                                                    placeholder="Ex.: o defeito voltou após a entrega")),
            field("Previsão de entrega", rx.input(type="date", name="due_date", class_name="input"),
                  "Opcional; sem informar, 7 dias."),
            dialog_actions("Abrir em garantia"),
            on_submit=S.confirm_warranty,
            class_name="stack-form",
        ),
    )


def _status_button(status) -> rx.Component:
    return rx.button(
        rx.cond(status == CANCELLED, "Cancelar ordem", "Mover para " + status),
        on_click=S.change_status(status),
        loading=S.is_loading,
        class_name=rx.cond(status == CANCELLED, "btn btn-danger", "btn btn-primary"),
    )


def _workflow() -> rx.Component:
    return panel(
        panel_header("Andamento"),
        rx.cond(
            S.next_status.length() > 0,
            rx.flex(rx.foreach(S.next_status, _status_button), gap="12px", wrap="wrap"),
            rx.text(
                rx.cond(S.permissions["read_only_reason"] != "", S.permissions["read_only_reason"],
                        "Não há próximos status disponíveis para o seu perfil."),
                class_name="muted",
            ),
        ),
        rx.box(
            rx.text("Técnico responsável", class_name="form-label"),
            options_select("technician", S.technicians, "Atribuir técnico", value=S.order["technician_id"],
                           on_change=S.assign_technician, disabled=S.permissions["technician_changeable"] == ""),
            class_name="field narrow-field",
        ),
    )


def _diagnosis() -> rx.Component:
    return panel(
        panel_header("Diagnóstico técnico"),
        rx.cond(
            S.permissions["budget_editable"] == "1",
            rx.form(
                rx.text_area(name="diagnosis", default_value=S.diagnosis, placeholder="Descreva o diagnóstico técnico",
                             class_name="input", aria_label="Diagnóstico técnico", key=S.diagnosis),
                submit_button("Salvar diagnóstico"),
                on_submit=S.save_diagnosis,
                class_name="stack-form",
            ),
            rx.cond(
                S.diagnosis != "",
                rx.text(S.diagnosis),
                rx.text("O diagnóstico pode ser registrado a partir do status Em análise.", class_name="muted"),
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
        rx.table.cell(
            rx.cond(S.permissions["budget_editable"] == "1",
                    small_button("Remover", "danger", on_click=S.remove_item(item["id"])))
        ),
    )


def _budget() -> rx.Component:
    t = S.totals
    return panel(
        panel_header("Orçamento"),
        table(["Tipo", "Descrição", "Qtd.", "Valor unitário", "Subtotal", ""], S.items, _item_row,
              "Nenhum item no orçamento."),
        rx.cond(
            S.permissions["budget_editable"] == "1",
            rx.form(
                rx.grid(
                    field("Tipo", values_select("kind", ["Serviço", "Peça"], "Tipo", value=S.item_kind,
                                                on_change=S.set_item_kind)),
                    rx.cond(
                        S.item_kind == "Peça",
                        field("Peça do estoque",
                              options_select("part_select", S.part_select_options, "Escolha a peça",
                                             value=S.item_part, on_change=S.set_item_part),
                              "Peças do estoque usam nome e preço do catálogo e dão baixa na quantidade."),
                    ),
                    rx.cond(
                        S.uses_stock_part,
                        rx.fragment(),
                        field("Descrição", text_input("description", "Ex.: SSD 480 GB", required=True)),
                    ),
                    field("Quantidade", text_input("quantity", "1", default_value="1",
                                                   disabled=S.item_kind == "Serviço"), "Serviços contam 1."),
                    rx.cond(
                        S.uses_stock_part,
                        rx.fragment(),
                        field("Valor unitário (R$)", text_input("unit_price", "Ex.: 250,00", required=True)),
                    ),
                    columns=rx.breakpoints(initial="1", md="2", xl="4"),
                    spacing="3",
                    width="100%",
                ),
                submit_button("Adicionar item"),
                on_submit=S.add_item,
                reset_on_submit=False,
                key=S.item_form_key,
                class_name="stack-form",
            ),
            rx.text("O orçamento pode ser alterado em Em análise, Aguardando aprovação e Em reparo.",
                    class_name="muted tiny"),
        ),
        rx.grid(
            _info("Serviços", t["services"]),
            _info("Peças", t["parts"]),
            _info("Total", t["total"]),
            _info("Pago", t["paid"]),
            _info(t["balance_label"], t["balance"]),
            columns=rx.breakpoints(initial="2", md="5"),
            spacing="4",
            width="100%",
            class_name="totals-grid",
        ),
    )


def _payment_row(payment) -> rx.Component:
    return rx.table.row(
        rx.table.cell(payment["paid_at"]),
        rx.table.cell(payment["method"]),
        rx.table.cell(payment["amount"]),
    )


def _payments() -> rx.Component:
    return panel(
        panel_header("Pagamentos"),
        table(["Data", "Forma", "Valor"], S.payments, _payment_row, "Nenhum pagamento registrado."),
        rx.cond(
            S.permissions["payments_allowed"] == "1",
            rx.form(
                rx.grid(
                    field("Valor (R$)", text_input("amount", "Ex.: 100,00", required=True),
                          rx.text("Saldo: ", S.totals["balance"])),
                    field("Forma de pagamento", values_select("method", list(PAYMENT_METHODS), "Selecione",
                                                              required=True)),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="3",
                    width="100%",
                ),
                submit_button("Registrar pagamento"),
                on_submit=S.add_payment,
                reset_on_submit=False,
                key=S.payment_form_key,
                class_name="stack-form",
            ),
        ),
    )


def _event(event) -> rx.Component:
    return rx.box(
        rx.box(class_name="timeline-dot"),
        rx.box(
            rx.flex(rx.text(event["kind"], class_name="timeline-kind"), rx.spacer(),
                    rx.text(event["at"], " · ", event["author"], class_name="muted tiny"), wrap="wrap", gap="8px"),
            rx.text(event["description"]),
            class_name="timeline-body",
        ),
        class_name="timeline-item",
    )


def _timeline() -> rx.Component:
    return panel(
        panel_header("Histórico de alterações"),
        rx.box(rx.foreach(S.timeline, _event), class_name="timeline"),
    )


def _cancel_dialog() -> rx.Component:
    return form_dialog(
        "Cancelar ordem de serviço",
        "Informe o motivo. O cancelamento fica registrado no histórico.",
        S.cancel_open,
        S.set_cancel_open,
        rx.form(
            field("Motivo do cancelamento", rx.text_area(name="reason", class_name="input",
                                                         placeholder="Ex.: cliente não aprovou o orçamento")),
            dialog_actions("Confirmar cancelamento"),
            on_submit=S.confirm_cancel,
            class_name="stack-form",
        ),
    )


def _rating() -> rx.Component:
    """Avaliação do cliente (add-service-rating)."""
    r = S.rating
    return rx.cond(
        r["score"] != "",
        panel(
            panel_header("Avaliação do cliente"),
            rx.flex(rx.text(r["score"], class_name="rating-score"), rx.text(r["group"], class_name=r["group_class"]),
                    rx.text("Avaliada em ", r["at"], class_name="muted tiny"), gap="12px", align="center", wrap="wrap"),
            rx.cond(r["comment"] != "", rx.text("\u201c", r["comment"], "\u201d", class_name="rating-comment")),
        ),
    )


def order_detail_page() -> rx.Component:
    return admin_shell(
        rx.cond(S.found, S.code, "Ordem de serviço"),
        "Acompanhe e atualize cada etapa do atendimento.",
        rx.cond(
            S.found,
            rx.vstack(
                rx.link("🧾 Comprovante (imprimir / PDF)", href="/admin/ordens/" + S.code + "/comprovante",
                        class_name="btn btn-outline"),
                _summary(),
                rx.grid(_workflow(), _diagnosis(), columns=rx.breakpoints(initial="1", lg="2"), spacing="4",
                        width="100%"),
                _budget(),
                _payments(),
                _rating(),
                _timeline(),
                _cancel_dialog(),
                _warranty_dialog(),
                spacing="5",
                width="100%",
            ),
            rx.cond(
                S.data_error == "",
                panel(empty_state("Ordem de serviço não encontrada."),
                      rx.link("← Voltar à lista de ordens", href="/admin/ordens", class_name="accent-link")),
            ),
        ),
        back=("Ordens de serviço", "/admin/ordens"),
    )
