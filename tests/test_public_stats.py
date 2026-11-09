"""Números reais na página inicial (mudança add-public-stats)."""

import httpx
import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.errors import ServiceUnavailableError, UnexpectedError
from assistencia_tech.data.xano import XanoClient, build_xano_gateway, mappers
from assistencia_tech.data.xano.limits import RequestPacer, ResponseCache
from assistencia_tech.models import OrderStatus, PublicStats
from assistencia_tech.presenters import home_stats
from assistencia_tech.services import public_stats as stats_service

pytestmark = pytest.mark.anyio


@pytest.fixture(autouse=True)
def _clean_cache():
    stats_service.clear_public_stats_cache()
    yield
    stats_service.clear_public_stats_cache()


async def test_demo_counts_match_the_orders():
    gateway = build_demo_gateway(lambda: 2026)
    orders = await gateway.orders.list()
    stats = await gateway.portal.public_stats()
    assert stats.delivered == sum(1 for o in orders if o.status == OrderStatus.DELIVERED)
    assert stats.in_progress == sum(1 for o in orders
                                    if o.status not in (OrderStatus.DELIVERED, OrderStatus.CANCELLED))
    assert (stats.ratings, stats.promoters, stats.detractors) == (1, 1, 0)  # nota 9 no seed


def test_home_cards_match_the_spec_example():
    row = home_stats(PublicStats(delivered=3, in_progress=2, ratings=3, promoters=2, detractors=1))
    assert row == {"delivered": "3", "in_progress": "2", "nps": "+33", "nps_hint": "NPS de 3 avaliações"}
    assert home_stats(PublicStats(delivered=0, in_progress=0, ratings=1, promoters=0, detractors=1))["nps"] == "-100"
    assert home_stats(PublicStats(delivered=1, in_progress=0, ratings=0, promoters=0, detractors=0))["nps"] == "—"


def test_unavailable_backend_shows_dashes_never_fake_numbers():
    row = home_stats(None)
    assert row["delivered"] == row["in_progress"] == row["nps"] == "—"


class _CountingPortal:
    def __init__(self, fail=False):
        self.calls, self.fail = 0, fail

    async def public_stats(self):
        self.calls += 1
        if self.fail:
            raise ServiceUnavailableError()
        return PublicStats(delivered=1, in_progress=1, ratings=0, promoters=0, detractors=0)


class _Gateway:
    def __init__(self, portal):
        self.portal = portal


async def test_backend_is_called_once_every_five_minutes():
    gateway, clock = _Gateway(_CountingPortal()), [1000.0]
    for _ in range(5):
        assert await stats_service.public_stats(gateway, now=lambda: clock[0]) is not None
    assert gateway.portal.calls == 1
    clock[0] += stats_service.CACHE_SECONDS + 1
    await stats_service.public_stats(gateway, now=lambda: clock[0])
    assert gateway.portal.calls == 2


async def test_failure_returns_none_and_is_not_cached():
    gateway = _Gateway(_CountingPortal(fail=True))
    assert await stats_service.public_stats(gateway) is None
    assert await stats_service.public_stats(gateway) is None
    assert gateway.portal.calls == 2


def test_xano_mapping_rejects_unexpected_shapes():
    record = {"entregues": 4, "em_atendimento": 2, "avaliacoes": 1, "promotores": 1, "detratores": 0}
    assert mappers.public_stats_from(record) == PublicStats(delivered=4, in_progress=2, ratings=1, promoters=1,
                                                            detractors=0)
    with pytest.raises(UnexpectedError):
        mappers.public_stats_from({"entregues": 4})


async def test_xano_calls_the_public_endpoint_without_token():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path, request.headers.get("authorization")))
        return httpx.Response(200, json={"entregues": 4, "em_atendimento": 2, "avaliacoes": 1, "promotores": 1,
                                         "detratores": 0})

    client = XanoClient("https://exemplo.invalid", 5, transport=httpx.MockTransport(handler),
                        pacer=RequestPacer(10_000, 1), cache=ResponseCache(0))
    gateway = build_xano_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"), client=client)
    stats = await gateway.portal.public_stats()
    assert stats.delivered == 4
    assert seen == [("GET", "/api:assistencia-tech-os/estatisticas_publicas", None)]
