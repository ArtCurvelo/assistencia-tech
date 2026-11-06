"""Estrutura das páginas públicas e administrativas."""

from __future__ import annotations

import reflex as rx

from ..state.base import AppState
from .ui import button, data_error_alert, data_source_pill, feedback_message

ADMIN_NAV = [
    ("▦", "Visão geral", "/admin"),
    ("♙", "Clientes", "/admin/clientes"),
    ("▣", "Equipamentos", "/admin/equipamentos"),
    ("☷", "Ordens de serviço", "/admin/ordens"),
]


def brand() -> rx.Component:
    return rx.link(
        rx.flex(
            rx.box("⚡", class_name="brand-icon"),
            rx.box(rx.text("ASSISTÊNCIA", class_name="brand-name"), rx.text("TECH", class_name="brand-sub")),
            align="center",
            gap="10px",
        ),
        href="/",
        class_name="brand-link",
    )


def public_header() -> rx.Component:
    return rx.box(
        rx.box(
            brand(),
            rx.spacer(),
            rx.flex(
                rx.link("Início", href="/"),
                rx.link("Serviços", href="/servicos"),
                rx.link("Painel", href="/admin"),
                class_name="public-nav",
                gap="28px",
            ),
            rx.spacer(),
            rx.flex(
                rx.link(button("Entrar", outline=True), href="/login"),
                rx.link(button("Criar conta"), href="/cadastro"),
                class_name="header-actions",
                gap="10px",
            ),
            class_name="header-inner page-width",
        ),
        class_name="public-header",
    )


def footer() -> rx.Component:
    return rx.box(
        rx.box(
            rx.heading("Assistência TECH", size="4"),
            rx.text("Tecnologia funcionando do jeito que deve.", class_name="muted tiny"),
        ),
        rx.text("Projeto acadêmico • versão 1.0", class_name="muted tiny"),
        class_name="footer page-width",
    )


def public_page(*children) -> rx.Component:
    return rx.box(public_header(), *children, footer(), class_name="app-root")


def _sidebar() -> rx.Component:
    return rx.box(
        brand(),
        rx.text(rx.cond(AppState.is_demo, "GESTÃO • DEMO", "GESTÃO"), class_name="sidebar-caption"),
        rx.vstack(
            *[
                rx.link(rx.text(icon, class_name="nav-icon"), rx.text(label), href=href, class_name="side-link")
                for icon, label, href in ADMIN_NAV
            ],
            spacing="2",
        ),
        rx.spacer(),
        rx.link("← Voltar ao site", href="/", class_name="side-back"),
        class_name="sidebar",
    )


def admin_shell(title, subtitle, *children, back: tuple[str, str] | None = None) -> rx.Component:
    heading = [rx.text("PAINEL ADMINISTRATIVO", class_name="eyebrow")]
    if back:
        heading = [rx.link(f"← {back[0]}", href=back[1], class_name="back-link")]
    return rx.box(
        rx.box(
            _sidebar(),
            rx.box(
                rx.box(
                    rx.box(*heading, rx.heading(title, size="8"), rx.text(subtitle, class_name="muted")),
                    rx.box(data_source_pill()),
                    class_name="admin-topbar",
                ),
                rx.vstack(data_error_alert(), feedback_message(), *children, spacing="5", class_name="admin-content"),
                class_name="admin-main",
            ),
            class_name="admin-layout",
        ),
        class_name="app-root admin-root",
    )
