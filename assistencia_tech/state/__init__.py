"""Estados Reflex, organizados por área da aplicação."""

from .base import AdminState, AppState
from .clients import ClientDetailState, ClientState
from .equipment import EquipmentState
from .inventory import InventoryState
from .order_detail import OrderDetailState
from .orders import OrderState
from .portal import PortalOrderState, PortalState
from .public import LoginState, RegisterState, TrackingState

__all__ = [
    "AdminState",
    "AppState",
    "ClientDetailState",
    "ClientState",
    "EquipmentState",
    "InventoryState",
    "LoginState",
    "OrderDetailState",
    "OrderState",
    "PortalOrderState",
    "PortalState",
    "RegisterState",
    "TrackingState",
]
