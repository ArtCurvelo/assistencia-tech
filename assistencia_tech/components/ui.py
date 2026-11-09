"""Elementos de interface reutilizáveis (botões, cartões, feedback e campos)."""

from __future__ import annotations

import reflex as rx

from ..state.base import AppState


def button(label: str, outline: bool = False, **props) -> rx.Component:
    return rx.button(label, class_name="btn btn-outline" if outline else "btn btn-primary", **props)


def small_button(label, variant: str = "ghost", **props) -> rx.Component:
    """Botão compacto para ações em tabelas (``ghost`` ou ``danger``)."""
    return rx.button(label, class_name=f"btn-sm btn-sm-{variant}", type="button", **props)


def submit_button(label: str) -> rx.Component:
    """Botão de envio que indica carregamento e evita envios duplicados."""
    return rx.button(
        label,
        type="submit",
        loading=AppState.is_loading,
        disabled=AppState.is_loading,
        class_name="btn btn-primary",
    )


def stat_card(value, label: str, hint: str = "") -> rx.Component:
    return rx.box(
        rx.text(value, class_name="stat-value"),
        rx.text(label, class_name="stat-label"),
        rx.text(hint, class_name="stat-hint") if hint else rx.fragment(),
        class_name="stat-card",
    )


def section_heading(eyebrow: str, title: str, subtitle: str) -> rx.Component:
    return rx.box(
        rx.text(eyebrow, class_name="eyebrow"),
        rx.heading(title, size="8"),
        rx.text(subtitle, class_name="muted"),
        class_name="section-heading",
    )


def status_badge(status, css_class) -> rx.Component:
    return rx.text(status, class_name=css_class)


def payment_badge(status, css_class) -> rx.Component:
    return rx.text(status, class_name=css_class)


def field(label: str, child: rx.Component, hint: str = "") -> rx.Component:
    return rx.el.label(
        rx.text(label, class_name="form-label"),
        child,
        rx.text(hint, class_name="field-hint") if hint else rx.fragment(),
        class_name="field",
    )


def text_input(name: str, placeholder: str = "", **props) -> rx.Component:
    return rx.input(name=name, placeholder=placeholder, class_name="input", **props)


def options_select(name: str, options, placeholder: str, **props) -> rx.Component:
    """Select cujas opções são dicionários ``{"value", "label"}`` (lista ou Var)."""
    if isinstance(options, list):
        items = [rx.select.item(o["label"], value=o["value"]) for o in options]
    else:
        items = [rx.foreach(options, lambda o: rx.select.item(o["label"], value=o["value"]))]
    return rx.select.root(
        rx.select.trigger(placeholder=placeholder, class_name="input select-trigger"),
        rx.select.content(*items),
        name=name,
        **props,
    )


def values_select(name: str, values: list[str], placeholder: str, **props) -> rx.Component:
    return options_select(name, [{"value": v, "label": v} for v in values], placeholder, **props)


def empty_state(message: str) -> rx.Component:
    return rx.box(rx.text(message, class_name="muted"), class_name="empty-state")


def panel(*children, **props) -> rx.Component:
    return rx.box(*children, class_name="panel-card " + props.pop("class_name", ""), **props)


def panel_header(title: str, *actions) -> rx.Component:
    return rx.flex(rx.heading(title, size="5"), rx.spacer(), *actions, align="center", wrap="wrap", gap="12px",
                   class_name="panel-header")


def data_source_pill() -> rx.Component:
    """Identifica a fonte de dados ativa; o modo demonstração é sempre destacado."""
    return rx.text(
        AppState.data_source_label,
        class_name=rx.cond(AppState.is_demo, "demo-pill", "source-pill"),
        title="Fonte de dados ativa",
    )


def data_error_alert() -> rx.Component:
    return rx.cond(
        AppState.data_error != "",
        rx.box(
            rx.text("Não foi possível carregar os dados", class_name="alert-title"),
            rx.text(AppState.data_error),
            class_name="alert alert-error",
            role="alert",
        ),
    )


def feedback_message() -> rx.Component:
    return rx.cond(
        AppState.feedback_message != "",
        rx.text(
            AppState.feedback_message,
            class_name="feedback feedback-" + AppState.feedback_kind,
            role="status",
        ),
    )


def table(headers: list[str], rows, render, empty_message: str) -> rx.Component:
    """Tabela com cabeçalho fixo, rolagem horizontal própria e estado vazio."""
    return rx.box(
        rx.table.root(
            rx.table.header(rx.table.row(*[rx.table.column_header_cell(h) for h in headers])),
            rx.table.body(rx.foreach(rows, render)),
            width="100%",
            variant="surface",
        ),
        rx.cond(rows.length() == 0, empty_state(empty_message)),
        class_name="table-wrap",
    )
