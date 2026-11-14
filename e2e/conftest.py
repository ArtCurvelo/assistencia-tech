"""Testes de ponta a ponta: um navegador real contra o site em modo demonstração.

O site precisa estar no ar antes (veja o README, seção "Testes de ponta a ponta").
``E2E_BASE_URL`` indica o endereço; o padrão é o servidor de produção local.
"""

import os
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
expect.set_options(timeout=15_000)


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def login(page: Page, base_url: str):
    """Entra por uma conta do acesso rápido da demonstração (ex.: "Atendente")."""

    def _login(role: str) -> Page:
        page.goto(f"{base_url}/login")
        page.locator("button.demo-account", has_text=role).click()
        expect(page).not_to_have_url(re.compile(r"/login"), timeout=20_000)
        # Espera a área do usuário carregar (como uma pessoa faria) antes de seguir para outra página.
        expect(page.get_by_role("button", name="Sair")).to_be_visible(timeout=20_000)
        return page

    return _login
