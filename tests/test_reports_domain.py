import csv
import io
from datetime import date, datetime
from decimal import Decimal

import pytest

from assistencia_tech.data.demo import seed
from assistencia_tech.data.demo.users import seed_users
from assistencia_tech.data.errors import ValidationError
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.csv_export import BOM, COLUMNS, csv_filename, orders_csv
from assistencia_tech.domain.reports import (
    build_report,
    default_period,
    make_period,
    orders_in_period,
)
from assistencia_tech.domain.staff_rules import (
    ensure_admin_remains,
    ensure_not_self,
    ensure_technician_can_leave,
    parse_staff_role,
)
from assistencia_tech.models import Role

ORDERS = seed.seed_orders()
TECHS = seed.seed_technicians()
OCTOBER = make_period(date(2026, 10, 1), date(2026, 10, 31))


# ------------------------------------------------------------- colaboradores
def test_parse_staff_role():
    assert parse_staff_role("Técnico") == Role.TECHNICIAN
    with pytest.raises(ValidationError, match="Cargo inválido"):
        parse_staff_role("Cliente")


def test_cannot_act_on_self():
    with pytest.raises(ValidationError, match="própria"):
        ensure_not_self("1", "1", "Não é possível desativar a própria conta.")
    ensure_not_self("1", "2", "x")


def test_last_active_admin_is_protected():
    users = seed_users()  # um único administrador (id 1)
    with pytest.raises(ValidationError, match="ao menos um administrador"):
        ensure_admin_remains(users, "1", Role.ADMIN, False)
    with pytest.raises(ValidationError, match="ao menos um administrador"):
        ensure_admin_remains(users, "1", Role.ATTENDANT, True)
    # Promover outro administrador libera a alteração.
    promoted = [u.model_copy(update={"role": Role.ADMIN}) if u.id == "2" else u for u in users]
    ensure_admin_remains(promoted, "1", Role.ADMIN, False)


def test_technician_with_open_orders_cannot_leave():
    with pytest.raises(ValidationError, match="2 ordens em aberto"):
        ensure_technician_can_leave(2)
    ensure_technician_can_leave(0)


# ---------------------------------------------------------------- relatórios
def test_period_validation_and_default():
    with pytest.raises(ValidationError, match="Período inválido"):
        make_period(date(2026, 11, 2), date(2026, 11, 1))
    period = default_period(date(2026, 11, 6))
    assert period.start == date(2026, 8, 8) and period.end == date(2026, 11, 6)


def test_period_is_inclusive_in_brasilia_time():
    period = make_period(date(2026, 10, 1), date(2026, 10, 1))
    assert period.contains(datetime(2026, 10, 1, 23, 59, tzinfo=BRT))
    assert not period.contains(datetime(2026, 10, 2, 0, 0, tzinfo=BRT))


def test_report_on_seed_data():
    report = build_report(ORDERS, TECHS, OCTOBER)
    v = report.volume
    assert (v.opened, v.delivered, v.cancelled, v.in_progress) == (7, 1, 1, 5)
    r = report.revenue
    assert r.total == Decimal("325.00")
    assert r.by_method["PIX"] == Decimal("325.00") and r.by_method["Dinheiro"] == Decimal("0.00")
    assert (r.delivered_count, r.average_ticket) == (1, Decimal("225.00"))
    rows = {row.name: (row.assigned, row.finished, row.budget_total) for row in report.technicians}
    assert rows == {
        "Diego Martins": (2, 2, Decimal("436.00")),
        "Carlos Mendes": (3, 0, Decimal("1835.00")),
        "Fernanda Rocha": (1, 0, Decimal("0.00")),
    }
    assert report.technicians[0].name == "Diego Martins"
    # 00120: 01/10 09:00 -> 03/10 16:00; 00122: 08/10 10:00 -> 10/10 17:00 (≈ 2,29 dias cada)
    assert report.turnaround.count == 2 and report.turnaround.average_days == 2.3


def test_report_outside_seed_period_is_empty():
    report = build_report(ORDERS, TECHS, make_period(date(2025, 1, 1), date(2025, 1, 31)))
    assert report.volume.opened == 0 and report.revenue.total == Decimal("0.00")
    assert report.revenue.average_ticket is None and report.turnaround.average_days is None
    assert report.technicians == ()


def test_payments_count_by_payment_date():
    # O pagamento de 00120 ocorreu em 04/10; o período de 04/10 a 04/10 só contém ele.
    report = build_report(ORDERS, TECHS, make_period(date(2026, 10, 4), date(2026, 10, 4)))
    assert report.revenue.total == Decimal("225.00")
    assert report.volume.opened == 0


# ----------------------------------------------------------------------- CSV
def _maps():
    clients = {c.id: c for c in seed.seed_clients()}
    equipment = {e.id: e for e in seed.seed_equipment()}
    return clients, equipment, {t.id: t for t in TECHS}


def test_csv_format():
    text = orders_csv(orders_in_period(ORDERS, OCTOBER), *_maps())
    assert text.startswith(BOM)
    rows = list(csv.reader(io.StringIO(text[1:]), delimiter=";"))
    assert tuple(rows[0]) == COLUMNS
    assert len(rows) == 8
    first = rows[1]
    assert first[0] == "OS-2026-00120" and first[1] == "01/10/2026 09:00"
    assert first[2] == "Camila Souza" and first[5] == "Diego Martins" and first[6] == "Entregue"
    assert first[7:] == ["225,00", "225,00", "0,00"]


def test_csv_quotes_separator_and_quotes():
    order = ORDERS[0].model_copy(update={"problem": 'Tela; "piscando"\nàs vezes'})
    text = orders_csv([order], *_maps())
    assert '"Tela; ""piscando""\nàs vezes"' in text
    rows = list(csv.reader(io.StringIO(text[1:]), delimiter=";"))
    assert len(rows) == 2 and len(rows[1]) == len(COLUMNS)
    assert rows[1][4] == 'Tela; "piscando"\nàs vezes'


def test_csv_filename():
    assert csv_filename(date(2026, 10, 1), date(2026, 10, 31)) == "ordens-2026-10-01-a-2026-10-31.csv"
