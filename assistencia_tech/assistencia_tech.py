"""Ponto de entrada do Reflex: cria o app e registra as rotas.

Páginas administrativas e do portal verificam sessão e permissão no
``on_load`` antes de carregar qualquer dado.
"""

import reflex as rx
from reflex import constants

from .pages.admin import reports_page, staff_page
from .pages.clients import client_detail_page, clients_page
from .pages.dashboard import dashboard_page
from .pages.equipment import equipment_page
from .pages.inventory import inventory_page
from .pages.order_detail import order_detail_page
from .pages.orders import orders_page
from .pages.portal import portal_order_page, portal_page
from .pages.receipt import portal_receipt_page, receipt_page, tracking_link_page
from .pages.public import access_denied_page, home_page, login_page, not_found_page, register_page, services_page
from .state.admin import ReportsState, StaffState
from .state.receipt import PortalReceiptState, ReceiptState, TrackingLinkState
from .state import (
    AdminState,
    AppState,
    ClientDetailState,
    ClientState,
    EquipmentState,
    InventoryState,
    LoginState,
    OrderDetailState,
    OrderState,
    PortalOrderState,
    PortalState,
    RegisterState,
)

SUFFIX = " | Assistência TECH"

app = rx.App(
    stylesheets=["/style.css"],
    theme=rx.theme(appearance="dark", accent_color="green", radius="medium"),
    head_components=[rx.el.link(rel="icon", href="/logo.svg", type="image/svg+xml")],
)

# Públicas
app.add_page(home_page, route="/", title="Início" + SUFFIX, on_load=AppState.load_session)
app.add_page(services_page, route="/servicos", title="Serviços" + SUFFIX, on_load=AppState.load_session)
app.add_page(login_page, route="/login", title="Entrar" + SUFFIX, on_load=LoginState.load_login)
app.add_page(register_page, route="/cadastro", title="Criar conta" + SUFFIX, on_load=RegisterState.load_register)
app.add_page(tracking_link_page, route="/consulta/[codigo]", title="Consulta da ordem" + SUFFIX,
             on_load=TrackingLinkState.load_tracking_link)
app.add_page(access_denied_page, route="/acesso-negado", title="Acesso negado" + SUFFIX,
             on_load=AppState.load_session)
app.add_page(not_found_page, route=constants.Page404.SLUG, title="Página não encontrada" + SUFFIX,
             on_load=AppState.load_session)

# Portal do cliente
app.add_page(portal_page, route="/minha-conta", title="Minha conta" + SUFFIX, on_load=PortalState.load_portal)
app.add_page(portal_order_page, route="/minha-conta/ordens/[codigo]", title="Minha ordem" + SUFFIX,
             on_load=PortalOrderState.load_portal_order)
app.add_page(portal_receipt_page, route="/minha-conta/ordens/[codigo]/comprovante", title="Comprovante" + SUFFIX,
             on_load=PortalReceiptState.load_portal_receipt)

# Administração
app.add_page(dashboard_page, route="/admin", title="Painel" + SUFFIX, on_load=AdminState.load_admin_data)
app.add_page(clients_page, route="/admin/clientes", title="Clientes" + SUFFIX, on_load=ClientState.load_admin_data)
app.add_page(client_detail_page, route="/admin/clientes/[cliente_id]", title="Cliente" + SUFFIX,
             on_load=ClientDetailState.load_client)
app.add_page(equipment_page, route="/admin/equipamentos", title="Equipamentos" + SUFFIX,
             on_load=EquipmentState.load_admin_data)
app.add_page(orders_page, route="/admin/ordens", title="Ordens de serviço" + SUFFIX,
             on_load=OrderState.load_admin_data)
app.add_page(order_detail_page, route="/admin/ordens/[codigo]", title="Ordem de serviço" + SUFFIX,
             on_load=OrderDetailState.load_order)
app.add_page(receipt_page, route="/admin/ordens/[codigo]/comprovante", title="Comprovante" + SUFFIX,
             on_load=ReceiptState.load_receipt)
app.add_page(inventory_page, route="/admin/estoque", title="Estoque" + SUFFIX,
             on_load=InventoryState.load_inventory)
app.add_page(reports_page, route="/admin/relatorios", title="Relatórios" + SUFFIX, on_load=ReportsState.load_reports)
app.add_page(staff_page, route="/admin/colaboradores", title="Colaboradores" + SUFFIX, on_load=StaffState.load_staff)
