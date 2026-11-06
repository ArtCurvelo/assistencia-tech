"""Carregamento conjunto dos dados usados pelas telas administrativas."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..data.repositories import DataGateway
from ..models import Client, Equipment, ServiceOrder, Technician


@dataclass(frozen=True)
class Catalog:
    clients: list[Client]
    equipment: list[Equipment]
    technicians: list[Technician]
    orders: list[ServiceOrder]
    clients_by_id: dict[str, Client] = field(init=False)
    equipment_by_id: dict[str, Equipment] = field(init=False)
    technicians_by_id: dict[str, Technician] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "clients_by_id", {c.id: c for c in self.clients})
        object.__setattr__(self, "equipment_by_id", {e.id: e for e in self.equipment})
        object.__setattr__(self, "technicians_by_id", {t.id: t for t in self.technicians})


async def load_catalog(gateway: DataGateway) -> Catalog:
    return Catalog(
        clients=await gateway.clients.list(),
        equipment=await gateway.equipment.list(),
        technicians=await gateway.technicians.list(),
        orders=await gateway.orders.list(),
    )
