"""Exportação CSV compatível com planilhas em português.

Separador ``;``, vírgula decimal e UTF-8 com BOM (o Excel reconhece a
codificação). O módulo ``csv`` protege campos com ``;``, aspas e quebras de
linha usando aspas.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable, Mapping
from decimal import Decimal

from ..models import Client, Equipment, ServiceOrder, Technician
from .clock import format_datetime
from .pricing import compute_totals
from .validators import quantize

BOM = "﻿"
COLUMNS = (
    "Código", "Abertura", "Cliente", "Equipamento", "Problema relatado", "Técnico", "Status", "Total", "Pago", "Saldo",
)


def decimal_br(value: Decimal) -> str:
    return f"{quantize(value):.2f}".replace(".", ",")


def orders_csv(
    orders: Iterable[ServiceOrder],
    clients: Mapping[str, Client],
    equipment: Mapping[str, Equipment],
    technicians: Mapping[str, Technician],
) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writerow(COLUMNS)
    for order in orders:
        totals = compute_totals(order)
        client = clients.get(order.client_id)
        item = equipment.get(order.equipment_id)
        technician = technicians.get(order.technician_id or "")
        writer.writerow(
            (
                order.code,
                format_datetime(order.opened_at),
                client.name if client else "",
                item.description if item else "",
                order.problem,
                technician.name if technician else "",
                order.status.value,
                decimal_br(totals.total),
                decimal_br(totals.paid),
                decimal_br(totals.balance),
            )
        )
    return BOM + buffer.getvalue()


def csv_filename(start, end) -> str:
    return f"ordens-{start.isoformat()}-a-{end.isoformat()}.csv"
