"""Configuração de publicação (mudança add-public-deployment)."""

import importlib
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_rxconfig(monkeypatch, **env):
    for name in ("ASSISTENCIA_PUBLIC_URL", "RENDER_EXTERNAL_URL", "REFLEX_API_URL", "REFLEX_DEPLOY_URL"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    import rxconfig

    return importlib.reload(rxconfig).config


def test_render_url_becomes_the_api_and_site_address(monkeypatch):
    config = load_rxconfig(monkeypatch, RENDER_EXTERNAL_URL="https://assistencia-tech.onrender.com/")
    assert config.api_url == "https://assistencia-tech.onrender.com"
    assert config.deploy_url == "https://assistencia-tech.onrender.com"


def test_explicit_public_url_wins_over_render(monkeypatch):
    config = load_rxconfig(monkeypatch, ASSISTENCIA_PUBLIC_URL="https://assistencia.exemplo.com.br",
                           RENDER_EXTERNAL_URL="https://assistencia-tech.onrender.com")
    assert config.api_url == "https://assistencia.exemplo.com.br"


def test_development_keeps_reflex_defaults_and_no_telemetry(monkeypatch):
    config = load_rxconfig(monkeypatch)
    assert config.api_url.startswith("http://localhost:")
    assert config.telemetry_enabled is False


def test_render_blueprint_uses_xano_without_secrets():
    blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "ASSISTENCIA_DATA_SOURCE" in blueprint and "value: xano" in blueprint
    lowered = blueprint.lower()
    assert not any(word in lowered for word in ("password", "senha", "token", "secret", "sync: false"))
    docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:3.14" in docker and "reflex export --frontend-only --no-zip --env prod" in docker
    # Ao iniciar, nada é recompilado (512 MB no plano gratuito): só o Granian com o frontend montado.
    assert "__REFLEX_SKIP_COMPILE=true" in docker and "__REFLEX_MOUNT_FRONTEND_COMPILED_APP=true" in docker
    assert "granian" in docker and "assistencia_tech.assistencia_tech:app" in docker


@pytest.fixture(autouse=True)
def _restore_rxconfig():
    yield
    import rxconfig

    importlib.reload(rxconfig)
