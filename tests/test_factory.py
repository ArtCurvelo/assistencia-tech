import pytest

from assistencia_tech.config import Settings
from assistencia_tech.data import factory
from assistencia_tech.data.errors import ConfigurationError


@pytest.fixture(autouse=True)
def _reset():
    factory.reset_gateway()
    yield
    factory.reset_gateway()


def test_builds_demo_gateway():
    gateway = factory.build_gateway(Settings(data_source="demo"))
    assert gateway.is_demo and gateway.label == "Modo demonstração"


def test_builds_xano_gateway_when_configured():
    gateway = factory.build_gateway(Settings(data_source="xano", xano_base_url="https://exemplo.invalid"))
    assert gateway.source == "xano" and not gateway.is_demo


def test_xano_without_base_url_never_falls_back_to_demo():
    with pytest.raises(ConfigurationError):
        factory.build_gateway(Settings(data_source="xano"))


def test_get_gateway_reads_environment_and_caches(monkeypatch):
    monkeypatch.delenv("ASSISTENCIA_DATA_SOURCE", raising=False)
    first = factory.get_gateway()
    assert first.is_demo
    assert factory.get_gateway() is first


def test_get_gateway_raises_for_incomplete_xano(monkeypatch):
    monkeypatch.setenv("ASSISTENCIA_DATA_SOURCE", "xano")
    monkeypatch.delenv("XANO_BASE_URL", raising=False)
    with pytest.raises(ConfigurationError):
        factory.get_gateway()
