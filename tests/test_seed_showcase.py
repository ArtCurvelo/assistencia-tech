"""O roteiro de povoamento da vitrine segue as regras do sistema (ensaio no modo demonstração)."""

from collections import Counter

import pytest

from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.demo.users import DEMO_PASSWORDS
from assistencia_tech.models import OrderStatus
from tools import seed_showcase as seed

pytestmark = pytest.mark.anyio


async def test_seed_runs_through_the_real_rules():
    gateway = build_demo_gateway(lambda: 2026)
    before = {o.code for o in await gateway.orders.list()}
    seeder = seed.Seeder(gateway, log=lambda *_: None)
    attendant = await seeder.login("atendimento@assistencia.test", DEMO_PASSWORDS["atendimento@assistencia.test"])
    techs = [await seeder.login(e, DEMO_PASSWORDS[e]) for e in ("carlos@assistencia.test", "fernanda@assistencia.test")]
    passwords = await seeder.run(attendant, techs)

    new = [o for o in await gateway.orders.list() if o.code not in before]
    assert len(new) == len(seed.ORDERS)
    by_status = Counter(o.status for o in new)
    assert by_status[OrderStatus.DELIVERED] == 6 and by_status[OrderStatus.CANCELLED] == 2
    assert sum(1 for o in new if o.rating) == 5  # avaliações feitas pelos próprios clientes
    assert all(o.payments for o in new if o.status == OrderStatus.DELIVERED)
    refused = next(o for o in new if o.status == OrderStatus.CANCELLED and o.items)
    assert refused.cancel_reason.startswith("Orçamento recusado pelo cliente")
    # Peças do estoque baixadas pelos orçamentos
    parts = {p.code: p for p in await gateway.parts.list()}
    assert parts["TELA-S23"].quantity == 1 and parts["SSD-480-NV"].quantity == 5
    assert len(passwords) == sum(1 for _, account in seed.CLIENTS if account)
    assert all(email.endswith("@exemplo.test") for email in passwords)


def test_generated_cpfs_are_valid():
    import random

    from assistencia_tech.domain.validators import normalize_cpf

    rng = random.Random(1)
    for _ in range(50):
        assert normalize_cpf(seed.cpf(rng))
