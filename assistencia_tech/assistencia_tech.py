import reflex as rx
from .state import AppState
from .models import EQUIPMENT_KINDS, ORDER_STATUSES
from .components import (
    brand, public_header, footer, button, stat_card, status_badge,
    field, admin_shell, section_heading, empty_state, submit_button
)

def home_page() -> rx.Component:
    services = [
        ("💻", "Computadores", "Formatação, limpeza, upgrades e diagnóstico."),
        ("🎮", "Consoles", "Manutenção preventiva e diagnóstico de falhas."),
        ("📱", "Celulares", "Análise de hardware, software e funcionamento."),
        ("💾", "Armazenamento", "Instalação de SSDs e migração de sistema."),
    ]
    return rx.box(
        public_header(),
        rx.box(
            rx.box(
                rx.text("⚡ ASSISTÊNCIA ESPECIALIZADA", class_name="eyebrow"),
                rx.heading("Seu equipamento", rx.text("funcionando de novo.", as_="span", class_name="accent"), size="9", class_name="hero-title"),
                rx.text("Manutenção, diagnóstico e reparos para computadores, notebooks, consoles, celulares e outros dispositivos.", class_name="hero-copy"),
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
                rx.box(rx.box(class_name="status-dot"), rx.text("Demonstração acadêmica • dados fictícios"), class_name="status-line"),
                rx.text("🛠️", class_name="hero-emoji"),
                rx.heading("Diagnóstico técnico", size="6"),
                rx.text("Identificamos o problema antes de realizar qualquer reparo, com transparência em cada etapa.", class_name="muted"),
                rx.divider(class_name="divider"),
                rx.flex(rx.text("✓ Transparência", class_name="accent-small"), rx.text("✓ Segurança", class_name="accent-small"), gap="18px"),
                class_name="hero-card",
            ),
            class_name="hero-grid page-width",
        ),
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
            section_heading("NOSSOS SERVIÇOS", "Soluções para seus dispositivos", "Do diagnóstico ao reparo, cuidamos do seu equipamento."),
            rx.grid(
                *[
                    rx.box(
                        rx.box(icon, class_name="service-icon"),
                        rx.heading(title, size="4"),
                        rx.text(desc, class_name="muted"),
                        rx.link("Saiba mais →", href="/servicos", class_name="accent-link"),
                        class_name="service-card",
                    )
                    for icon, title, desc in services
                ],
                columns="4",
                spacing="4",
            ),
            class_name="section page-width",
        ),
        rx.box(
            rx.box(
                rx.text("ACOMPANHE SEU EQUIPAMENTO", class_name="eyebrow"),
                rx.heading("Saiba em que etapa está o seu reparo.", size="7"),
                rx.text("Consulte uma ordem de serviço usando o código fornecido no atendimento.", class_name="muted"),
            ),
            rx.box(
                rx.text("Código da Ordem de Serviço", class_name="form-label"),
                rx.input(value=AppState.tracking_code, on_change=AppState.set_tracking_code, placeholder="Ex.: OS-2026-00125", class_name="input"),
                rx.button("Consultar", on_click=AppState.lookup_order, class_name="btn btn-primary"),
                rx.cond(AppState.tracking_message != "", rx.text(AppState.tracking_message, class_name="notice notice-" + AppState.tracking_kind, role="status"), rx.box()),
                class_name="tracking-box",
            ),
            class_name="tracking page-width",
        ),
        rx.box(
            rx.heading("Seu equipamento precisa de ajuda?", size="7"),
            rx.text("Conheça nossos serviços e veja como funciona o atendimento."),
            rx.link(button("Ver serviços →"), href="/servicos"),
            class_name="cta",
        ),
        footer(),
        class_name="app-root",
    )

def services_page() -> rx.Component:
    data = [
        ("💻", "Computadores e notebooks", "Diagnóstico e manutenção de computadores e notebooks.", ["Formatação", "Instalação de sistema", "Limpeza interna", "Troca de componentes", "Upgrade de memória", "Instalação de SSD"]),
        ("🎮", "Consoles", "Manutenção e diagnóstico de consoles.", ["Limpeza interna", "Manutenção preventiva", "Diagnóstico", "Temperatura", "Conectividade"]),
        ("📱", "Smartphones", "Diagnóstico e manutenção de dispositivos móveis.", ["Diagnóstico", "Problemas de software", "Configuração", "Recuperação do sistema"]),
    ]
    return rx.box(
        public_header(),
        rx.box(rx.text("SERVIÇOS", class_name="eyebrow"), rx.heading("O que podemos fazer pelo seu equipamento?", size="9"), rx.text("Serviços técnicos para diversos tipos de dispositivos.", class_name="muted"), class_name="page-header page-width"),
        rx.vstack(
            *[
                rx.box(
                    rx.text(icon, class_name="service-large-icon"),
                    rx.box(
                        rx.heading(title, size="6"),
                        rx.text(desc, class_name="muted"),
                        rx.flex(*[rx.text("✓ " + item, class_name="service-chip") for item in items], wrap="wrap", gap="10px"),
                    ),
                    class_name="service-large",
                )
                for icon, title, desc, items in data
            ],
            spacing="4",
            class_name="services-list page-width",
        ),
        footer(),
        class_name="app-root",
    )

def login_page() -> rx.Component:
    return rx.box(
        public_header(),
        rx.center(
            rx.box(
                rx.box(rx.text("⚡", class_name="auth-icon"), rx.heading("Bem-vindo de volta", size="7"), rx.text("Entre na sua conta para acompanhar seus serviços.", class_name="muted"), class_name="auth-heading"),
                rx.form(
                    rx.text("E-mail", class_name="form-label"),
                    rx.input(name="email", type="email", placeholder="seu@email.com", required=True, class_name="input"),
                    rx.text("Senha", class_name="form-label"),
                    rx.input(name="senha", type="password", placeholder="Digite sua senha", required=True, class_name="input"),
                    rx.button("Entrar na demonstração", type="submit", class_name="btn btn-primary full-width"),
                    on_submit=AppState.demo_login,
                    reset_on_submit=False,
                ),
                rx.text(AppState.auth_message, class_name="notice"),
                rx.text("Autenticação real ainda não conectada às APIs.", class_name="muted tiny"),
                rx.text("Ainda não possui uma conta?"),
                rx.link("Criar conta", href="/cadastro", class_name="accent-link"),
                class_name="auth-card",
            ),
            class_name="auth-container",
        ),
        footer(),
        class_name="app-root",
    )

def register_page() -> rx.Component:
    return rx.box(
        public_header(),
        rx.center(
            rx.box(
                rx.box(rx.text("+", class_name="auth-icon"), rx.heading("Criar sua conta", size="7"), rx.text("Cadastre-se para acompanhar seus equipamentos.", class_name="muted"), class_name="auth-heading"),
                rx.form(
                    rx.text("Nome completo", class_name="form-label"),
                    rx.input(name="nome", placeholder="Seu nome", required=True, class_name="input"),
                    rx.text("E-mail", class_name="form-label"),
                    rx.input(name="email", type="email", placeholder="seu@email.com", required=True, class_name="input"),
                    rx.text("Telefone", class_name="form-label"),
                    rx.input(name="telefone", placeholder="(11) 99999-9999", required=True, class_name="input"),
                    rx.text("Senha", class_name="form-label"),
                    rx.input(name="senha", type="password", placeholder="Crie uma senha", required=True, class_name="input"),
                    rx.button("Criar conta (demo)", type="submit", class_name="btn btn-primary full-width"),
                    on_submit=AppState.demo_register,
                    reset_on_submit=False,
                ),
                rx.text(AppState.auth_message, class_name="notice"),
                rx.text("Cadastro demonstrativo: os dados não são enviados a um servidor.", class_name="muted tiny"),
                rx.text("Já possui uma conta?"),
                rx.link("Entrar", href="/login", class_name="accent-link"),
                class_name="auth-card",
            ),
            class_name="auth-container",
        ),
        footer(),
        class_name="app-root",
    )

def recent_order_row(order: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(order["code"]),
        rx.table.cell(order["client"]),
        rx.table.cell(order["device"]),
        rx.table.cell(status_badge(order["status"])),
    )

def client_row(client: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(client["name"]),
        rx.table.cell(client["email"]),
        rx.table.cell(client["phone"]),
    )

def equipment_row(equipment: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(equipment["client"]),
        rx.table.cell(equipment["kind"]),
        rx.table.cell(equipment["model"]),
    )

def order_row(order: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(order["code"]),
        rx.table.cell(order["client"]),
        rx.table.cell(order["device"]),
        rx.table.cell(order["problem"]),
        rx.table.cell(status_badge(order["status"])),
        rx.table.cell(
            rx.select(
                list(ORDER_STATUSES),
                value=order["status"],
                on_change=lambda value: AppState.update_order_status(order["code"], value),
                class_name="input status-select",
            )
        ),
    )

def dashboard_page() -> rx.Component:
    return admin_shell(
        "Visão geral",
        "Acompanhe a operação da assistência em um só lugar.",
        rx.grid(
            stat_card(AppState.orders.length(), "Ordens cadastradas"),
            stat_card(AppState.open_orders, "Ordens em andamento"),
            stat_card(AppState.clients.length(), "Clientes"),
            stat_card(AppState.equipment.length(), "Equipamentos"),
            columns="4",
            spacing="4",
        ),
        rx.box(
            rx.flex(rx.heading("Ordens recentes", size="5"), rx.spacer(), rx.link("Ver todas →", href="/admin/ordens", class_name="accent-link"), align="center"),
            rx.table.root(
                rx.table.header(rx.table.row(rx.table.column_header_cell("Código"), rx.table.column_header_cell("Cliente"), rx.table.column_header_cell("Equipamento"), rx.table.column_header_cell("Status"))),
                rx.table.body(rx.foreach(AppState.orders, recent_order_row)),
                width="100%",
                variant="surface",
            ),
            rx.cond(AppState.orders.length() == 0, empty_state("Nenhuma ordem de serviço registrada.")),
            class_name="panel-card",
        ),
        rx.cond(AppState.is_demo, rx.box(rx.text("Dados demonstrativos", class_name="demo-label"), rx.text("Os registros exibidos são fictícios e existem apenas enquanto a aplicação estiver em execução.", class_name="muted tiny"), class_name="demo-notice")),
    )

def clients_page() -> rx.Component:
    return admin_shell(
        "Clientes",
        "Consulte e cadastre clientes da assistência.",
        rx.box(
            rx.heading("Novo cliente", size="4"),
            rx.form(
                rx.grid(
                    rx.box(rx.text("Nome", class_name="form-label"), rx.input(name="name", placeholder="Nome completo", required=True, class_name="input")),
                    rx.box(rx.text("E-mail", class_name="form-label"), rx.input(name="email", type="email", placeholder="cliente@email.com", required=True, class_name="input")),
                    rx.box(rx.text("Telefone", class_name="form-label"), rx.input(name="phone", placeholder="(11) 99999-9999", class_name="input")),
                    columns="3",
                    spacing="3",
                ),
                submit_button("Adicionar cliente"),
                on_submit=AppState.add_client,
                reset_on_submit=True,
            ),
            class_name="panel-card",
        ),
        rx.box(
            rx.flex(rx.heading("Lista de clientes", size="5"), rx.spacer(), rx.input(value=AppState.client_search, on_change=AppState.set_client_search, placeholder="Buscar por nome ou e-mail…", class_name="input search-input"), align="center", wrap="wrap", gap="3"),
            rx.table.root(
                rx.table.header(rx.table.row(rx.table.column_header_cell("Nome"), rx.table.column_header_cell("E-mail"), rx.table.column_header_cell("Telefone"))),
                rx.table.body(rx.foreach(AppState.filtered_clients, client_row)),
                width="100%",
                variant="surface",
            ),
            rx.cond(AppState.filtered_clients.length() == 0, empty_state("Nenhum cliente encontrado."), rx.box()),
            class_name="panel-card",
        ),
    )

def equipment_page() -> rx.Component:
    return admin_shell(
        "Equipamentos",
        "Registre os aparelhos recebidos para manutenção.",
        rx.box(
            rx.heading("Cadastrar equipamento", size="4"),
            rx.form(
                rx.grid(
                    rx.box(rx.text("Cliente", class_name="form-label"), rx.select(AppState.client_names, name="client", placeholder="Selecione o cliente", required=True, class_name="input")),
                    rx.box(rx.text("Tipo", class_name="form-label"), rx.select(list(EQUIPMENT_KINDS), name="kind", placeholder="Tipo de aparelho", required=True, class_name="input")),
                    rx.box(rx.text("Marca/modelo", class_name="form-label"), rx.input(name="model", placeholder="Ex.: Lenovo IdeaPad", required=True, class_name="input")),
                    columns="3",
                    spacing="3",
                ),
                submit_button("Adicionar equipamento"),
                on_submit=AppState.add_equipment,
                reset_on_submit=True,
            ),
            class_name="panel-card",
        ),
        rx.box(
            rx.heading("Equipamentos cadastrados", size="5"),
            rx.table.root(
                rx.table.header(rx.table.row(rx.table.column_header_cell("Cliente"), rx.table.column_header_cell("Tipo"), rx.table.column_header_cell("Marca/modelo"))),
                rx.table.body(rx.foreach(AppState.equipment, equipment_row)),
                width="100%",
                variant="surface",
            ),
            rx.cond(AppState.equipment.length() == 0, empty_state("Nenhum equipamento cadastrado.")),
            class_name="panel-card",
        ),
    )

def orders_page() -> rx.Component:
    return admin_shell(
        "Ordens de serviço",
        "Acompanhe o fluxo de atendimento e atualize o status.",
        rx.box(
            rx.heading("Abrir ordem de serviço", size="4"),
            rx.form(
                rx.grid(
                    rx.box(rx.text("Cliente", class_name="form-label"), rx.select(AppState.client_names, name="client", placeholder="Selecione o cliente", required=True, class_name="input")),
                    rx.box(rx.text("Equipamento", class_name="form-label"), rx.input(name="device", placeholder="Ex.: Notebook Lenovo", required=True, class_name="input")),
                    rx.box(rx.text("Problema relatado", class_name="form-label"), rx.input(name="problem", placeholder="Descreva o defeito", required=True, class_name="input")),
                    columns="3",
                    spacing="3",
                ),
                submit_button("Criar ordem"),
                on_submit=AppState.add_order,
                reset_on_submit=True,
            ),
            class_name="panel-card",
        ),
        rx.box(
            rx.flex(rx.heading("Ordens registradas", size="5"), rx.spacer(), rx.input(value=AppState.order_search, on_change=AppState.set_order_search, placeholder="Buscar código, cliente ou equipamento…", class_name="input search-input"), align="center", wrap="wrap", gap="3"),
            rx.table.root(
                rx.table.header(rx.table.row(rx.table.column_header_cell("Código"), rx.table.column_header_cell("Cliente"), rx.table.column_header_cell("Equipamento"), rx.table.column_header_cell("Problema"), rx.table.column_header_cell("Status"), rx.table.column_header_cell("Ação"))),
                rx.table.body(rx.foreach(AppState.filtered_orders, order_row)),
                width="100%",
                variant="surface",
            ),
            rx.cond(AppState.filtered_orders.length() == 0, empty_state("Nenhuma ordem encontrada."), rx.box()),
            class_name="panel-card",
        ),
        rx.box(rx.text("Fluxo sugerido: Recebido → Em análise → Em reparo → Concluído.", class_name="muted tiny")),
    )

app = rx.App(
    stylesheets=["/style.css"],
)
app.add_page(home_page, route="/", title="Início | Assistência TECH")
app.add_page(services_page, route="/servicos", title="Serviços | Assistência TECH")
app.add_page(login_page, route="/login", title="Login | Assistência TECH")
app.add_page(register_page, route="/cadastro", title="Cadastro | Assistência TECH")
app.add_page(dashboard_page, route="/admin", title="Painel | Assistência TECH", on_load=AppState.load_admin_data)
app.add_page(clients_page, route="/admin/clientes", title="Clientes | Assistência TECH", on_load=AppState.load_admin_data)
app.add_page(equipment_page, route="/admin/equipamentos", title="Equipamentos | Assistência TECH", on_load=AppState.load_admin_data)
app.add_page(orders_page, route="/admin/ordens", title="Ordens de serviço | Assistência TECH", on_load=AppState.load_admin_data)
