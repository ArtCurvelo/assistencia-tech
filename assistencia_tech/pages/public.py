"""Páginas públicas: início, serviços, login e cadastro."""

from __future__ import annotations

import reflex as rx

from ..components import button, feedback_message, field, public_page, section_heading, stat_card
from ..state import AppState, LoginState, RegisterState, TrackingState

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


def _auth_card(icon: str, title: str, subtitle: str, *children) -> rx.Component:
    return rx.center(
        rx.box(
            rx.box(rx.text(icon, class_name="auth-icon"), rx.heading(title, size="7"),
                   rx.text(subtitle, class_name="muted"), class_name="auth-heading"),
            feedback_message(),
            *children,
            class_name="auth-card",
        ),
        class_name="auth-container",
    )


def _auth_input(label: str, name: str, hint: str = "", **props) -> rx.Component:
    return field(label, rx.input(name=name, required=True, class_name="input", **props), hint)


def _auth_submit(label: str) -> rx.Component:
    return rx.button(label, type="submit", loading=AppState.is_loading, disabled=AppState.is_loading,
                     class_name="btn btn-primary full-width")


def _demo_card(account) -> rx.Component:
    return rx.button(
        rx.box(rx.text(account["label"], class_name="demo-account-role"),
               rx.text(account["description"], class_name="muted tiny")),
        on_click=LoginState.quick_login(account["key"]),
        disabled=LoginState.is_loading,
        type="button",
        class_name="demo-account",
        title=account["email"],
    )


def _demo_access() -> rx.Component:
    return rx.cond(
        LoginState.is_demo,
        rx.box(
            rx.text("ACESSO RÁPIDO • CONTAS DE DEMONSTRAÇÃO", class_name="demo-label"),
            rx.grid(rx.foreach(LoginState.demo_accounts, _demo_card), columns="2", spacing="2", width="100%"),
            rx.text("Disponível somente no modo demonstração. Senhas de teste em docs/DEMO_USERS.md.",
                    class_name="muted tiny"),
            class_name="demo-access",
        ),
    )


def login_page() -> rx.Component:
    form = rx.form(
        _auth_input("E-mail", "email", type="email", placeholder="seu@email.com", custom_attrs={"autocomplete": "username"}),
        _auth_input("Senha", "password", type="password", placeholder="Digite sua senha",
                    custom_attrs={"autocomplete": "current-password"}),
        _auth_submit("Entrar"),
        on_submit=LoginState.login,
        reset_on_submit=False,
        class_name="stack-form",
    )
    return public_page(
        _auth_card(
            "⚡", "Bem-vindo de volta", "Entre para acessar sua área.",
            rx.cond(LoginState.login_notice != "", rx.text(LoginState.login_notice, class_name="notice notice-error")),
            form,
            _demo_access(),
            rx.flex(rx.text("Ainda não possui uma conta?"),
                    rx.link("Criar conta", href="/cadastro", class_name="accent-link"), gap="2", wrap="wrap"),
        ),
    )


def register_page() -> rx.Component:
    form = rx.form(
        _auth_input("Nome completo", "name", placeholder="Seu nome", custom_attrs={"autocomplete": "name"}),
        _auth_input("CPF", "cpf", "Com ou sem pontuação.", placeholder="000.000.000-00"),
        _auth_input("E-mail", "email", type="email", placeholder="seu@email.com", custom_attrs={"autocomplete": "email"}),
        _auth_input("Telefone", "phone", "Com DDD.", placeholder="(11) 98765-4321", custom_attrs={"autocomplete": "tel"}),
        _auth_input("Senha", "password", "Mínimo de 8 caracteres, com letras e números.", type="password",
                    custom_attrs={"autocomplete": "new-password"}),
        _auth_input("Confirme a senha", "password_confirm", type="password", custom_attrs={"autocomplete": "new-password"}),
        _auth_submit("Criar conta"),
        on_submit=RegisterState.register,
        reset_on_submit=False,
        class_name="stack-form",
    )
    return public_page(
        _auth_card(
            "+", "Criar sua conta", "Acompanhe seus equipamentos e ordens de serviço.",
            form,
            rx.flex(rx.text("Já possui uma conta?"), rx.link("Entrar", href="/login", class_name="accent-link"),
                    gap="2", wrap="wrap"),
        ),
    )


def access_denied_page() -> rx.Component:
    return public_page(
        rx.center(
            rx.box(
                rx.text("🔒", class_name="auth-icon"),
                rx.heading("Acesso negado", size="7"),
                rx.text("Seu perfil não tem permissão para acessar esta página.", class_name="muted"),
                rx.cond(
                    AppState.is_authenticated,
                    rx.link(button("Ir para a minha área"), href=AppState.user_home),
                    rx.link(button("Entrar"), href="/login"),
                ),
                class_name="auth-card auth-heading",
            ),
            class_name="auth-container",
        ),
    )


def not_found_page() -> rx.Component:
    return public_page(
        rx.center(
            rx.box(
                rx.text("404", class_name="not-found-code"),
                rx.heading("Página não encontrada", size="7"),
                rx.text("O endereço acessado não existe ou foi movido.", class_name="muted"),
                rx.flex(
                    rx.cond(
                        AppState.is_authenticated,
                        rx.link(button("Ir para a minha área"), href=AppState.user_home),
                        rx.link(button("Página inicial"), href="/"),
                    ),
                    gap="3",
                    justify="center",
                ),
                class_name="auth-card auth-heading",
            ),
            class_name="auth-container",
        ),
    )
