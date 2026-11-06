"""Roteiro de demonstração (docs/DEMO_SCRIPT.md) executado pelos serviços.

Garante que cada passo descrito no roteiro funciona com os dados de
demonstração, na mesma ordem e com os mesmos perfis da apresentação.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.demo.auth import DemoAuthProvider
from assistencia_tech.data.demo.users import DEMO_PASSWORDS, seed_users
from assistencia_tech.data.errors import AuthenticationError, PermissionDeniedError, ValidationError
from assistencia_tech.domain.clock import BRT
from assistencia_tech.domain.pricing import compute_totals
from assistencia_tech.models import OrderStatus
from assistencia_tech.services import (
    AuthService,
    EquipmentService,
    OrderService,
    PortalService,
    ReportService,
    StaffService,
    reset_auth_state,
)

pytestmark = pytest.mark.anyio
NOW = datetime(2026, 11, 6, 14, 0, tzinfo=BRT)


@pytest.fixture
def gw():
    gateway = build_demo_gateway(year_provider=lambda: 2026)
    object.__setattr__(gateway, "auth", DemoAuthProvider(seed_users(), iterations=1_000))
    reset_auth_state()
    yield gateway
    reset_auth_state()


async def test_demo_script_end_to_end(gw):
    auth = AuthService(gw)

    async def login(email: str):
        return (await auth.login(email, DEMO_PASSWORDS[email]))[1]

    # 1. Visitante: consulta pública sem dados pessoais.
    view = await OrderService(gw, None).public_view("OS-2026-00125")
    assert view.status == "Em reparo" and "Marina" not in str(view.model_dump())

    # 2. Login: mensagem genérica para senha errada.
    with pytest.raises(AuthenticationError, match="E-mail ou senha inválidos"):
        await auth.login("admin@assistencia.test", "errada123")

    # 3. Cliente faz o próprio cadastro.
    _, joana = await auth.register_client({
        "name": "Joana Teixeira", "cpf": "529.982.247-25", "email": "joana@exemplo.test",
        "phone": "(21) 99876-5432", "password": "joana2026", "password_confirm": "joana2026",
    })
    assert (await PortalService(gw, joana).my_orders()) == []

    # 4. Atendente cadastra o equipamento, abre a OS e atribui o técnico.
    paulo = await login("atendimento@assistencia.test")
    notebook = await EquipmentService(gw, paulo).create({
        "client_id": joana.client_id, "kind": "Notebook", "brand": "Dell", "model": "Inspiron 15",
        "serial_number": "DL-INS-2026",
    })
    attendant_orders = OrderService(gw, paulo, clock=lambda: NOW)
    order = await attendant_orders.open({
        "client_id": joana.client_id, "equipment_id": notebook.id, "problem": "Não liga após queda de energia",
    })
    code = order.code
    assert code == "OS-2026-00127"
    await attendant_orders.assign_technician(code, "1")  # Carlos Mendes
    with pytest.raises(PermissionDeniedError):
        await attendant_orders.record_diagnosis(code, "Atendente não diagnostica")

    # 5. Técnico diagnostica, orça e envia para aprovação; não altera ordem de outro técnico.
    carlos = await login("carlos@assistencia.test")
    tech_orders = OrderService(gw, carlos, clock=lambda: NOW)
    await tech_orders.change_status(code, "Em análise")
    with pytest.raises(ValidationError, match="diagnóstico"):
        await tech_orders.change_status(code, "Aguardando aprovação")
    await tech_orders.record_diagnosis(code, "Fonte de alimentação queimada.")
    await tech_orders.add_item(code, {"kind": "Serviço", "description": "Troca da fonte", "unit_price": "150,00"})
    await tech_orders.add_item(code, {"kind": "Peça", "description": "Fonte 65 W", "quantity": "1",
                                      "unit_price": "180,00"})
    await tech_orders.change_status(code, "Aguardando aprovação")
    with pytest.raises(PermissionDeniedError, match="outro técnico"):
        await tech_orders.record_diagnosis("OS-2026-00124", "Teste")

    # 6. Atendente registra a aprovação; técnico conclui; atendente recebe e entrega.
    await attendant_orders.change_status(code, "Em reparo")
    await tech_orders.change_status(code, "Concluído")
    await attendant_orders.add_payment(code, {"amount": "130,00", "method": "PIX"})
    with pytest.raises(ValidationError, match="R\\$ 200,00"):
        await attendant_orders.change_status(code, "Entregue")
    await attendant_orders.add_payment(code, {"amount": "200,00", "method": "Cartão de crédito"})
    delivered = await attendant_orders.change_status(code, "Entregue")
    totals = compute_totals(delivered)
    assert delivered.status == OrderStatus.DELIVERED
    assert (totals.total, totals.balance, totals.payment_status) == (Decimal("330.00"), Decimal("0.00"), "Pago")
    authors = {e.author for e in delivered.history}
    assert {"Paulo Nunes (Atendente)", "Carlos Mendes (Técnico)"} <= authors

    # 7. Cliente acompanha no portal.
    portal = await PortalService(gw, joana).my_orders()
    assert [p.order.code for p in portal] == [code] and portal[0].order.status == OrderStatus.DELIVERED

    # 8. Relatórios do período padrão (inclui o dia da demonstração).
    admin = await login("admin@assistencia.test")
    reports = ReportService(gw, admin, today=lambda: date(2026, 11, 6))
    report = await reports.report(reports.default_period())
    assert report.volume.opened == 8 and report.volume.delivered == 2
    assert report.revenue.total == Decimal("655.00")
    filename, content = await reports.export_csv(reports.default_period())
    assert filename == "ordens-2026-08-08-a-2026-11-06.csv" and code in content

    # 9. Colaboradores: proteção do técnico com ordens em aberto e novo cadastro.
    staff = StaffService(gw, admin)
    with pytest.raises(ValidationError, match="ordens em aberto"):
        await staff.set_active("3", False)
    bruno = await staff.create({"name": "Bruno Alves", "email": "bruno@assistencia.test", "role": "Técnico",
                                "specialty": "Impressoras", "password": "bruno2026"})
    assert bruno.technician_id is not None
