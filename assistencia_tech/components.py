import reflex as rx

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

def button(label: str, outline: bool = False) -> rx.Component:
    return rx.button(label, class_name="btn btn-outline" if outline else "btn btn-primary")

def public_header() -> rx.Component:
    return rx.box(
        rx.box(brand(), rx.spacer(), rx.flex(rx.link("Início", href="/"), rx.link("Serviços", href="/servicos"), rx.link("Painel", href="/admin"), class_name="public-nav", gap="28px"), rx.spacer(), rx.flex(rx.link(button("Entrar", outline=True), href="/login"), rx.link(button("Criar conta"), href="/cadastro"), class_name="header-actions", gap="10px"), class_name="header-inner page-width"),
        class_name="public-header",
    )

def footer() -> rx.Component:
    return rx.box(
        rx.box(rx.heading("Assistência TECH", size="4"), rx.text("Tecnologia funcionando do jeito que deve.", class_name="muted tiny")),
        rx.text("Protótipo acadêmico • versão 1.0", class_name="muted tiny"),
        class_name="footer page-width",
    )

def stat_card(value: str, label: str) -> rx.Component:
    return rx.box(rx.text(value, class_name="stat-value"), rx.text(label, class_name="stat-label"), class_name="stat-card")

def section_heading(eyebrow: str, title: str, subtitle: str) -> rx.Component:
    return rx.box(rx.text(eyebrow, class_name="eyebrow"), rx.heading(title, size="8"), rx.text(subtitle, class_name="muted"), class_name="section-heading")

def status_badge(status: str) -> rx.Component:
    return rx.badge(status, class_name="status-badge status-" + status.lower().replace(" ", "-"))

def field(label: str, child: rx.Component) -> rx.Component:
    return rx.box(rx.text(label, class_name="form-label"), child, class_name="field")

def empty_state(message: str) -> rx.Component:
    return rx.box(rx.text(message, class_name="muted"), class_name="empty-state")

def admin_shell(title: str, subtitle: str, *children) -> rx.Component:
    nav_items = [
        ("▦", "Visão geral", "/admin"),
        ("♙", "Clientes", "/admin/clientes"),
        ("▣", "Equipamentos", "/admin/equipamentos"),
        ("☷", "Ordens de serviço", "/admin/ordens"),
    ]
    return rx.box(
        rx.box(
            rx.box(brand(), rx.text("GESTÃO • DEMO", class_name="sidebar-caption"), rx.vstack(*[rx.link(rx.text(icon, class_name="nav-icon"), rx.text(label), href=href, class_name="side-link") for icon, label, href in nav_items], spacing="2"), rx.spacer(), rx.link("← Voltar ao site", href="/", class_name="side-back"), class_name="sidebar"),
            rx.box(
                rx.box(rx.box(rx.text("PAINEL ADMINISTRATIVO", class_name="eyebrow"), rx.heading(title, size="8"), rx.text(subtitle, class_name="muted")), rx.box(rx.text("DEMO", class_name="demo-pill")), class_name="admin-topbar"),
                rx.vstack(*children, spacing="5", class_name="admin-content"),
                class_name="admin-main",
            ),
            class_name="admin-layout",
        ),
        class_name="app-root admin-root",
    )
