"""Diálogos de edição e de confirmação."""

from __future__ import annotations

import reflex as rx

from ..state.base import AppState
from .ui import feedback_message


def form_dialog(title: str, description: str, open_var, on_open_change, form: rx.Component) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(title),
            rx.dialog.description(description, class_name="muted"),
            feedback_message(),
            form,
            class_name="dialog-card",
        ),
        open=open_var,
        on_open_change=on_open_change,
    )


def dialog_actions(submit_label: str) -> rx.Component:
    return rx.flex(
        rx.dialog.close(rx.button("Cancelar", type="button", class_name="btn btn-outline")),
        rx.button(submit_label, type="submit", loading=AppState.is_loading, class_name="btn btn-primary"),
        justify="end",
        gap="12px",
        class_name="dialog-actions",
    )


def confirm_dialog(title: str, message, open_var, on_open_change, on_confirm, confirm_label: str) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(title),
            rx.alert_dialog.description(message, class_name="muted"),
            rx.flex(
                rx.alert_dialog.cancel(rx.button("Cancelar", class_name="btn btn-outline")),
                rx.button(confirm_label, on_click=on_confirm, loading=AppState.is_loading, class_name="btn btn-danger"),
                justify="end",
                gap="12px",
                class_name="dialog-actions",
            ),
            class_name="dialog-card",
        ),
        open=open_var,
        on_open_change=on_open_change,
    )
