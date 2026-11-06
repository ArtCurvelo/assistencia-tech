"""Páginas públicas: início, serviços, login e cadastro."""

from __future__ import annotations

import reflex as rx

from ..components import button, public_page, section_heading, stat_card
from ..state import AuthState, TrackingState

HOME_SERVICES = [
    ("💻", "Computadores", "Formatação, limpeza, upgrades e diagnóstico."),
    ("🎮", "Consoles", "Manutenção preventiva e diagnóstico de falhas."),
    ("📱", "Celulares", "Análise de hardware, software e funcionamento."),
    ("💾", "Armazenamento", "Instalação de SSDs e migração de sistema."),
]

SERVICE_CATALOG = [
    ("💻", "Computadores e notebooks", "Diagnóstico e manutenção de computadores e notebooks.",
     ["Formatação", "Instalação de sistema", "Limpeza interna", "Troca de componentes", "Upgrade de memória",
      "Instalação de SSD"]),
    ("🎮", "Consoles", "Manutenção e diagnóstico de consoles.",
     ["Limpeza interna", "Manutenção preventiva", "Diagnóstico", "Temperatura", "Conectividade"]),
    ("📱", "Smartphones e tablets", "Diagnóstico e manutenção de dispositivos móveis.",
     ["Diagnóstico", "Problemas de software", "Configuração", "Recuperação do sistema"]),
]


def _hero() -> rx.Component:
    return rx.box(
        rx.box(
            rx.text("⚡ ASSISTÊNCIA ESPECIALIZADA", class_name="eyebrow"),
            rx.heading("Seu equipamento", rx.text("funcionando de novo.", as_="span", class_name="accent"),
                       size="9", class_name="hero-title"),
            rx.text("Manutenção, diagnóstico e reparos para computadores, notebooks, consoles, celulares e outros "
                    "dispositivos.", class_name="hero-copy"),
            rx.flex(
                rx.link(button("Conhecer serviços →"), href="/servicos"),
                rx.link(button("Área administrativa", outline=True), href="/admin"),
                class_name="hero-actions",
                wrap="wrap",
                gap="12px",
            ),
            class_name="hero-content",
        ),
        rx.box(
            rx.box(rx.box(class_name="status-dot"), rx.text("Demonstração acadêmica • dados fictícios"),
                   class_name="status-line"),
            rx.text("🛠️", class_name="hero-emoji"),
            rx.heading("Diagnóstico técnico", size="6"),
            rx.text("Identificamos o problema antes de realizar qualquer reparo, com transparência em cada etapa.",
                    class_name="muted"),
            rx.divider(class_name="divider"),
            rx.flex(rx.text("✓ Transparência", class_name="accent-small"),
                    rx.text("✓ Segurança", class_name="accent-small"), gap="18px"),
            class_name="hero-card",
        ),
        class_name="hero-grid page-width",
    )


def _tracking() -> rx.Component:
    result = TrackingState.result
    return rx.box(
        rx.box(
            rx.text("ACOMPANHE SEU EQUIPAMENTO", class_name="eyebrow"),
            rx.heading("Saiba em que etapa está o seu reparo.", size="7"),
            rx.text("Consulte uma ordem de serviço usando o código fornecido no atendimento.", class_name="muted"),
        ),
        rx.box(
            rx.el.label("Código da Ordem de Serviço", html_for="tracking-code", class_name="form-label"),
            rx.input(id="tracking-code", value=TrackingState.tracking_code,
                     on_change=TrackingState.set_tracking_code, placeholder="Ex.: OS-2026-00125", class_name="input"),
            rx.button("Consultar", on_click=TrackingState.lookup_order, class_name="btn btn-primary"),
            rx.cond(
                TrackingState.has_result,
                rx.box(
                    rx.text(result["code"], class_name="tracking-code"),
                    rx.text(result["status"], class_name="tracking-status"),
                    rx.text(result["equipment"], class_name="muted"),
                    rx.text("Última atualização: ", result["updated_at"], class_name="muted tiny"),
                    class_name="tracking-result",
                    role="status",
                ),
            ),
            rx.cond(
                TrackingState.tracking_message != "",
                rx.text(TrackingState.tracking_message, class_name="notice notice-" + TrackingState.tracking_kind,
                        role="status"),
            ),
            class_name="tracking-box",
        ),
        class_name="tracking page-width",
    )


def home_page() -> rx.Component:
    return public_page(
        _hero(),
        rx.grid(
            stat_card("+500", "Equipamentos reparados"),
            stat_card("98%", "Clientes satisfeitos"),
            stat_card("24h", "Meta de diagnóstico inicial"),
            stat_card("100%", "Transparência"),
            columns="4",
            spacing="0",
            class_name="stats-grid page-width",
        ),
        rx.box(
            section_heading("NOSSOS SERVIÇOS", "Soluções para seus dispositivos",
                            "Do diagnóstico ao reparo, cuidamos do seu equipamento."),
            rx.grid(
                *[
                    rx.box(
                        rx.box(icon, class_name="service-icon"),
                        rx.heading(title, size="4"),
                        rx.text(desc, class_name="muted"),
                        rx.link("Saiba mais →", href="/servicos", class_name="accent-link"),
                        class_name="service-card",
                    )
                    for icon, title, desc in HOME_SERVICES
                ],
                columns="4",
                spacing="4",
            ),
            class_name="section page-width",
        ),
        _tracking(),
        rx.box(
            rx.heading("Seu equipamento precisa de ajuda?", size="7"),
            rx.text("Conheça nossos serviços e veja como funciona o atendimento."),
            rx.link(button("Ver serviços →"), href="/servicos"),
            class_name="cta",
        ),
    )


def services_page() -> rx.Component:
    return public_page(
        rx.box(
            rx.text("SERVIÇOS", class_name="eyebrow"),
            rx.heading("O que podemos fazer pelo seu equipamento?", size="9"),
            rx.text("Serviços técnicos para diversos tipos de dispositivos.", class_name="muted"),
            class_name="page-header page-width",
        ),
        rx.vstack(
            *[
                rx.box(
                    rx.text(icon, class_name="service-large-icon"),
                    rx.box(
                        rx.heading(title, size="6"),
                        rx.text(desc, class_name="muted"),
                        rx.flex(*[rx.text("✓ " + item, class_name="service-chip") for item in items],
                                wrap="wrap", gap="10px"),
                    ),
                    class_name="service-large",
                )
                for icon, title, desc, items in SERVICE_CATALOG
            ],
            spacing="4",
            class_name="services-list page-width",
        ),
    )


def _auth_card(icon: str, title: str, subtitle: str, form: rx.Component, notice: str, switch) -> rx.Component:
    return rx.center(
        rx.box(
            rx.box(rx.text(icon, class_name="auth-icon"), rx.heading(title, size="7"),
                   rx.text(subtitle, class_name="muted"), class_name="auth-heading"),
            form,
            rx.text(AuthState.auth_message, class_name="notice"),
            rx.text(notice, class_name="muted tiny"),
            *switch,
            class_name="auth-card",
        ),
        class_name="auth-container",
    )


def _auth_input(label: str, name: str, **props) -> list[rx.Component]:
    return [rx.text(label, class_name="form-label"), rx.input(name=name, required=True, class_name="input", **props)]


def login_page() -> rx.Component:
    form = rx.form(
        *_auth_input("E-mail", "email", type="email", placeholder="seu@email.com"),
        *_auth_input("Senha", "senha", type="password", placeholder="Digite sua senha"),
        rx.button("Entrar na demonstração", type="submit", class_name="btn btn-primary full-width"),
        on_submit=AuthState.demo_login,
        reset_on_submit=False,
    )
    return public_page(
        _auth_card("⚡", "Bem-vindo de volta", "Entre na sua conta para acompanhar seus serviços.", form,
                   "Autenticação real ainda não conectada às APIs.",
                   [rx.text("Ainda não possui uma conta?"), rx.link("Criar conta", href="/cadastro",
                                                                     class_name="accent-link")]),
    )


def register_page() -> rx.Component:
    form = rx.form(
        *_auth_input("Nome completo", "nome", placeholder="Seu nome"),
        *_auth_input("E-mail", "email", type="email", placeholder="seu@email.com"),
        *_auth_input("Telefone", "telefone", placeholder="(11) 99999-9999"),
        *_auth_input("Senha", "senha", type="password", placeholder="Crie uma senha"),
        rx.button("Criar conta (demo)", type="submit", class_name="btn btn-primary full-width"),
        on_submit=AuthState.demo_register,
        reset_on_submit=False,
    )
    return public_page(
        _auth_card("+", "Criar sua conta", "Cadastre-se para acompanhar seus equipamentos.", form,
                   "Cadastro demonstrativo: os dados não são enviados a um servidor.",
                   [rx.text("Já possui uma conta?"), rx.link("Entrar", href="/login", class_name="accent-link")]),
    )
