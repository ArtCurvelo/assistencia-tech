"""Serviços de aplicação: orquestram validação, autorização, regras de domínio e persistência."""

from .auth import AuthService, SessionResult, reset_auth_state
from .catalog import Catalog, load_catalog
from .clients import ClientDetail, ClientService
from .equipment import EquipmentService
from .orders import OrderService
from .portal import PortalOrder, PortalService

__all__ = [
    "AuthService",
    "Catalog",
    "ClientDetail",
    "ClientService",
    "EquipmentService",
    "OrderService",
    "PortalOrder",
    "PortalService",
    "SessionResult",
    "load_catalog",
    "reset_auth_state",
]
