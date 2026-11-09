"""Comprovante da ordem para impressão ou PDF (add-order-receipt) e consulta pública por link."""

from __future__ import annotations

import reflex as rx

from ..components import data_error_alert, logo, public_page
from ..state.receipt import PortalReceiptState, ReceiptState, TrackingLinkState
from .public import tracking_box


def _info(label: str, value) -> rx.Component:
    return rx.box(rx.text(label, class_name="receipt-label"), rx.text(value, class_name="receipt-value"))


def _section(title: str, *children) -> rx.Component:
    return rx.box(rx.text(title, class_name="receipt-section-title"), *children, class_name="receipt-section")


def _items_table(state) -> rx.Component:
    return rx.el.table(
        rx.el.thead(rx.el.tr(rx.el.th("Tipo"), rx.el.th("Descrição"), rx.el.th("Qtd."),
                             rx.el.th("Unitário"), rx.el.th("Subtotal"))),
        rx.el.tbody(rx.foreach(state.items, lambda i: rx.el.tr(
            rx.el.td(i["kind"]), rx.el.td(i["description"]), rx.el.td(i["quantity"]),
            rx.el.td(i["unit_price"]), rx.el.td(i["subtotal"])))),
        class_name="receipt-table",
    )


def _delivery(state) -> rx.Component:
    r, t = state.receipt, state.totals
    return rx.fragment(
        _section(
            "Serviços e peças",
            rx.cond(state.items.length() > 0, _items_table(state),
                    rx.text("Nenhum item registrado.", class_name="receipt-value")),
            rx.grid(_info("Serviços", t["services"]), _info("Peças", t["parts"]), _info("Total", t["total"]),
                    _info("Pago", t["paid"]), _info("Situação", t["payment_status"]),
                    columns="5", class_name="receipt-grid"),
        ),
        _section(
            "Pagamentos",
            rx.cond(state.payments.length() > 0,
                    rx.vstack(rx.foreach(state.payments, lambda p: rx.text(
                        p["paid_at"], " — ", p["method"], " — ", p["amount"], class_name="receipt-value")),
                        spacing="1"),
                    rx.text("Nenhum pagamento registrado.", class_name="receipt-value")),
        ),
        _section(
            "Entrega e garantia",
            rx.grid(_info("Entregue em", r["delivered_at"]),
                    _info("Garantia até", rx.cond(r["warranty_until"] != "", r["warranty_until"], "Sem garantia")),
                    columns="2", class_name="receipt-grid"),
            rx.cond(r["warranty_until"] != "",
                    rx.text("Garantia de 90 dias para o serviço realizado (Código de Defesa do Consumidor, "
                            "art. 26, II). Apresente este comprovante ou o código da ordem.",
                            class_name="receipt-note")),
        ),
    )


def _sheet(state) -> rx.Component:
    r = state.receipt
    return rx.box(
        rx.flex(
            rx.box(
                rx.flex(logo("receipt-logo"), rx.text("Assistência TECH", class_name="receipt-brand"),
                        align="center", gap="8px"),
                rx.text("Projeto acadêmico • manutenção e reparo de equipamentos", class_name="receipt-note"),
                rx.heading(r["kind"], size="6", class_name="receipt-title"),
                rx.text(r["code"], class_name="receipt-code"),
            ),
            rx.box(
                rx.image(src=r["qr"], alt="QR code da consulta da ordem " + r["code"], class_name="receipt-qr"),
                rx.text("Acompanhe pelo QR code", class_name="receipt-note"),
                class_name="receipt-qr-box",
            ),
            justify="between",
            gap="16px",
        ),
        _section(
            "Ordem de serviço",
            rx.grid(_info("Aberta em", r["opened_at"]), _info("Status", r["status"]),
                    _info("Previsão de entrega", r["due_date"]), columns="3", class_name="receipt-grid"),
            rx.cond(r["warranty_of"] != "",
                    rx.text("Ordem em garantia da ", r["warranty_of"], ": sem cobrança.", class_name="receipt-note")),
            rx.cond(r["cancel_reason"] != "", _info("Motivo do cancelamento", r["cancel_reason"])),
        ),
        _section(
            "Cliente",
            rx.grid(_info("Nome", r["client"]), _info("CPF", r["cpf"]), _info("Telefone", r["phone"]),
                    columns="3", class_name="receipt-grid"),
        ),
        _section(
            "Equipamento",
            rx.grid(_info("Equipamento", r["equipment"]), _info("Número de série", r["serial"]),
                    columns="2", class_name="receipt-grid"),
            _info("Problema relatado", r["problem"]),
        ),
        rx.cond(r["is_delivery"] == "1", _delivery(state)),
        rx.box(
            rx.text("Consulta pública: ", r["tracking_url"], class_name="receipt-note receipt-url"),
            rx.grid(
                rx.box(rx.box(class_name="receipt-sign-line"), rx.text("Assinatura do cliente", class_name="receipt-note")),
                rx.box(rx.box(class_name="receipt-sign-line"),
                       rx.text("Assistência TECH", class_name="receipt-note")),
                columns="2", gap="32px", class_name="receipt-signatures",
            ),
        ),
        class_name="receipt-sheet",
    )


def _receipt_page(state, back_label: str) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.link("← " + back_label, href=state.back_href, class_name="accent-link"),
            rx.cond(state.found,
                    rx.button("🖨 Imprimir / salvar PDF", on_click=rx.call_script("window.print()"),
                              class_name="btn btn-primary")),
            justify="between", align="center", wrap="wrap", gap="12px",
            class_name="receipt-toolbar no-print",
        ),
        rx.box(data_error_alert(), class_name="no-print"),
        rx.cond(
            state.found,
            _sheet(state),
            rx.cond(state.data_error == "",
                    rx.box(rx.heading("Ordem não encontrada", size="5"),
                           rx.text("Confira o código da ordem de serviço.", class_name="muted"),
                           class_name="receipt-toolbar")),
        ),
        class_name="receipt-page",
    )


def receipt_page() -> rx.Component:
    return _receipt_page(ReceiptState, "Voltar à ordem")


def portal_receipt_page() -> rx.Component:
    return _receipt_page(PortalReceiptState, "Voltar à minha ordem")


def tracking_link_page() -> rx.Component:
    return public_page(tracking_box(TrackingLinkState))
