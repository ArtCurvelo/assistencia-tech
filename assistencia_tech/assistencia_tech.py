"""Ponto de entrada do Reflex: cria o app e registra as rotas."""

import reflex as rx

from .pages.clients import client_detail_page, clients_page
from .pages.dashboard import dashboard_page
from .pages.equipment import equipment_page
from .pages.order_detail import order_detail_page
from .pages.orders import orders_page
from .pages.public import home_page, login_page, register_page, services_page
from .state import AdminState, ClientDetailState, ClientState, EquipmentState, OrderDetailState, OrderState

SUFFIX = " | Assistência TECH"

app = rx.App(
    stylesheets=["/style.css"],
    theme=rx.theme(appearance="dark", accent_color="green", radius="medium"),
)

app.add_page(home_page, route="/", title="Início" + SUFFIX)
app.add_page(services_page, route="/servicos", title="Serviços" + SUFFIX)
app.add_page(login_page, route="/login", title="Login" + SUFFIX)
app.add_page(register_page, route="/cadastro", title="Cadastro" + SUFFIX)

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
