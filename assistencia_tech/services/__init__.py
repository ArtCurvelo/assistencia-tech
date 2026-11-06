"""Serviços de aplicação: orquestram validação, regras de domínio e persistência."""

from .catalog import Catalog, load_catalog
from .clients import ClientDetail, ClientService
from .equipment import EquipmentService
from .orders import OrderService

__all__ = ["Catalog", "ClientDetail", "ClientService", "EquipmentService", "OrderService", "load_catalog"]
