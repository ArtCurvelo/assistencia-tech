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
                class_name="public-nav",
                gap="28px",
            ),
            rx.spacer(),
            rx.cond(
                AppState.is_authenticated,
                rx.flex(
                    rx.text(AppState.user_name, class_name="header-user"),
                    rx.link(button("Minha área", outline=True), href=AppState.user_home),
                    button("Sair", on_click=AppState.logout),
                    class_name="header-actions",
                    gap="10px",
                    align="center",
                ),
                rx.flex(
                    rx.link(button("Entrar", outline=True), href="/login"),
                    rx.link(button("Criar conta"), href="/cadastro"),
                    class_name="header-actions",
                    gap="10px",
                ),
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


def skip_link() -> rx.Component:
    return rx.el.a("Pular para o conteúdo", href="#conteudo", class_name="skip-link")


def public_page(*children) -> rx.Component:
    return rx.box(
        skip_link(),
        public_header(),
        rx.box(*children, id="conteudo", tab_index=-1),
        footer(),
        class_name="app-root",
    )


def _nav_link(icon: str, label: str, href: str) -> rx.Component:
    return rx.link(rx.text(icon, class_name="nav-icon"), rx.text(label), href=href, class_name="side-link",
                   on_click=AppState.close_mobile_menu)


def _menu_toggle() -> rx.Component:
    return rx.el.button(
        rx.cond(AppState.mobile_menu_open, "✕", "☰"),
        on_click=AppState.toggle_mobile_menu,
        type="button",
        class_name="menu-toggle",
        aria_label=rx.cond(AppState.mobile_menu_open, "Fechar menu", "Abrir menu"),
        aria_controls="admin-nav",
        aria_expanded=rx.cond(AppState.mobile_menu_open, "true", "false"),
    )


def _sidebar() -> rx.Component:
    return rx.box(
        rx.box(brand(), _menu_toggle(), class_name="sidebar-top"),
        rx.box(
            rx.text(rx.cond(AppState.is_demo, "GESTÃO • DEMO", "GESTÃO"), class_name="sidebar-caption"),
            rx.el.nav(
                rx.vstack(
                    *[
                        rx.link(rx.text(icon, class_name="nav-icon"), rx.text(label), href=href,
                                class_name="side-link", on_click=AppState.close_mobile_menu)
                        for icon, label, href in ADMIN_NAV
                    ],
                    rx.cond(AppState.can_view_stock,
                            _nav_link("⚙", "Estoque", "/admin/estoque")),
                    rx.cond(AppState.can_view_reports,
                            _nav_link("▤", "Relatórios", "/admin/relatorios")),
                    rx.cond(AppState.can_manage_staff,
                            _nav_link("♟", "Colaboradores", "/admin/colaboradores")),
                    spacing="2",
                ),
                aria_label="Navegação administrativa",
            ),
            rx.spacer(),
            rx.box(
                rx.text(AppState.user_name, class_name="side-user-name"),
                rx.text(AppState.user_role, class_name="side-user-role"),
                rx.button("Sair", on_click=AppState.logout, class_name="btn-sm btn-sm-ghost side-logout"),
                class_name="side-user",
            ),
            rx.link("← Voltar ao site", href="/", class_name="side-back"),
            id="admin-nav",
            class_name="sidebar-body",
        ),
        class_name=rx.cond(AppState.mobile_menu_open, "sidebar sidebar-open", "sidebar"),
    )


def admin_shell(title, subtitle, *children, back: tuple[str, str] | None = None) -> rx.Component:
    heading = [rx.text("PAINEL ADMINISTRATIVO", class_name="eyebrow")]
    if back:
        heading = [rx.link(f"← {back[0]}", href=back[1], class_name="back-link")]
    return rx.box(
        skip_link(),
        rx.box(
            _sidebar(),
            rx.box(
                rx.box(
                    rx.box(*heading, rx.heading(title, size="8"), rx.text(subtitle, class_name="muted")),
                    rx.box(data_source_pill()),
                    class_name="admin-topbar",
                ),
                rx.vstack(data_error_alert(), feedback_message(), *children, spacing="5", class_name="admin-content"),
                id="conteudo",
                tab_index=-1,
                class_name="admin-main",
            ),
            class_name="admin-layout",
        ),
        class_name="app-root admin-root",
    )
