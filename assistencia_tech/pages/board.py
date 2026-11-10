"""Quadro Kanban das ordens de serviço (mudança add-orders-board)."""

from __future__ import annotations

import reflex as rx

from ..components import admin_shell
from ..models import ORDER_STATUSES
from ..state.board import BoardState


def _move_button(card, target: str) -> rx.Component:
    return rx.cond(
        card["moves"].contains("|" + target + "|"),
        rx.button(
            "→ " + target,
            on_click=BoardState.move(card["code"], target),
            disabled=BoardState.is_loading,
            type="button",
            class_name="board-move",
            aria_label="Mover " + card["code"] + " para " + target,
        ),
    )


def _card(card) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.link(card["code"], href="/admin/ordens/" + card["code"], class_name="code-link"),
            rx.cond(card["late"] != "", rx.text(card["late"], class_name="late-badge")),
            justify="between", align="center", gap="8px", wrap="wrap",
        ),
        rx.text(card["client"], class_name="board-client"),
        rx.text(card["equipment"], class_name="muted tiny"),
        rx.text("Técnico: ", card["technician"], class_name="muted tiny"),
        rx.flex(*[_move_button(card, status) for status in ORDER_STATUSES if status != "Cancelado"],
                gap="6px", wrap="wrap", class_name="board-moves"),
        class_name="board-card",
    )


def _column(index: int, status: str) -> rx.Component:
    column = BoardState.columns[index]
    return rx.box(
        rx.flex(
            rx.box(class_name="board-dot", style={"background": column["color"]}),
            rx.heading(status, size="3"),
            rx.text(column["count"], class_name="board-count"),
            align="center", gap="8px", class_name="board-column-header",
        ),
        rx.vstack(rx.foreach(BoardState.cards[status], _card), spacing="2", width="100%"),
        rx.cond(
            column["more"] != "",
            rx.link("+ ", column["more"], " ordem(ns) — ver lista completa", href="/admin/ordens",
                    class_name="accent-link tiny"),
        ),
        class_name="board-column",
        role="region",
        aria_label="Coluna " + status,
    )


def board_page() -> rx.Component:
    return admin_shell(
        "Quadro de ordens",
        "O fluxo da oficina em uma tela: mova cada ordem para a próxima etapa.",
        rx.cond(
            BoardState.columns.length() > 0,
            rx.box(*[_column(i, status) for i, status in enumerate(ORDER_STATUSES)], class_name="board"),
        ),
        rx.text("O cancelamento exige motivo e é feito no detalhe da ordem.", class_name="muted tiny"),
        back=("Ordens de serviço", "/admin/ordens"),
    )
