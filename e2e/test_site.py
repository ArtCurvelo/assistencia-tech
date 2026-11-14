"""Fluxos principais conferidos num navegador real (modo demonstração)."""

import re
import urllib.request

from playwright.sync_api import Page, expect


# ----------------------------------------------------------------------
# Site público
# ----------------------------------------------------------------------
def test_home_shows_real_numbers_and_no_admin_shortcut(page: Page, base_url: str):
    page.goto(base_url)
    cards = page.locator(".stats-grid .stat-card")
    expect(cards).to_have_count(4)
    expect(cards.nth(0)).to_contain_text("Equipamentos entregues")
    expect(cards.nth(0).locator(".stat-value")).to_have_text(re.compile(r"^\d+$"))
    expect(cards.nth(3)).to_contain_text("90 dias")
    expect(page.get_by_text("Área administrativa")).to_have_count(0)


def test_keyboard_reaches_the_skip_link_with_visible_focus(page: Page, base_url: str):
    """refine-frontend-experience 2.3: "Pular para o conteúdo" é o primeiro foco e fica visível."""
    page.goto(base_url)
    expect(page.locator(".stats-grid")).to_be_visible()
    page.keyboard.press("Tab")
    skip = page.locator("a.skip-link")
    expect(skip).to_be_focused()
    expect(skip).to_have_text("Pular para o conteúdo")
    assert skip.bounding_box()["y"] >= 0  # entrou na tela ao receber o foco
    page.keyboard.press("Tab")
    outline = page.evaluate("getComputedStyle(document.activeElement).outlineStyle")
    assert outline != "none"  # foco visível no elemento seguinte


def test_services_page_explains_the_flow_and_faq_opens(page: Page, base_url: str):
    page.goto(f"{base_url}/servicos")
    expect(page.locator(".step-card")).to_have_count(6)
    question = page.get_by_text("E se eu recusar o orçamento?")
    question.click()
    expect(page.get_by_text("cancelada sem cobrança do reparo")).to_be_visible()


def test_public_lookup_by_link(page: Page, base_url: str):
    page.goto(f"{base_url}/consulta/OS-2026-00120")
    result = page.locator(".tracking-result")
    expect(result).to_contain_text("OS-2026-00120")
    expect(result).to_contain_text("Entregue")
    page.goto(f"{base_url}/consulta/qualquer-coisa")
    expect(page.get_by_text("Código não encontrado")).to_be_visible()


def test_receipt_requires_login(page: Page, base_url: str):
    page.goto(f"{base_url}/admin/ordens/OS-2026-00120/comprovante")
    expect(page).to_have_url(re.compile(r"/login/?\?proximo="), timeout=20_000)


def test_dashboard_starts_with_dashes_before_loading(base_url: str):
    """refine-frontend-experience 3.3: a página entregue pelo servidor traz "—" nos indicadores."""
    html = urllib.request.urlopen(f"{base_url}/admin/", timeout=30).read().decode("utf-8")
    values = re.findall(r'class="[^"]*stat-value[^"]*"[^>]*>([^<]*)<', html)
    assert values and all(value.strip() == "—" for value in values), values


# ----------------------------------------------------------------------
# Equipe
# ----------------------------------------------------------------------
def test_attendant_dashboard_and_board(page: Page, base_url: str, login):
    login("Atendente")
    expect(page.get_by_role("heading", name=re.compile(r"^(Bom dia|Boa tarde|Boa noite), "))).to_be_visible()
    expect(page.get_by_role("heading", name="Precisa de atenção")).to_be_visible()
    expect(page.locator(".quick-action", has_text="Nova ordem")).to_be_visible()

    page.goto(f"{base_url}/admin/ordens/quadro")
    expect(page.locator(".board-column")).to_have_count(7)
    # Entrega sem quitação: recusada com a mensagem do sistema, e a ordem continua onde estava.
    page.get_by_role("button", name="Mover OS-2026-00122 para Entregue").click()
    expect(page.get_by_text("Registre o pagamento antes da entrega").first).to_be_visible()
    done = page.get_by_role("region", name="Coluna Concluído")
    expect(done.get_by_role("link", name="OS-2026-00122")).to_be_visible()


def test_technician_sees_own_queue_and_limited_shortcuts(page: Page, login):
    login("Técnico")
    expect(page.get_by_role("heading", name="Meus atendimentos")).to_be_visible()
    expect(page.locator(".quick-action", has_text="Estoque")).to_be_visible()
    expect(page.locator(".quick-action", has_text="Nova ordem")).to_have_count(0)


def test_receipt_has_qr_code_for_the_public_lookup(page: Page, base_url: str, login):
    login("Atendente")
    page.goto(f"{base_url}/admin/ordens/OS-2026-00120/comprovante")
    expect(page.get_by_role("heading", name="Comprovante de entrega")).to_be_visible()
    expect(page.locator(".receipt-url")).to_contain_text("/consulta/OS-2026-00120")
    qr = page.locator("img.receipt-qr")
    assert qr.get_attribute("src").startswith("data:image/svg+xml")
    expect(page.locator(".receipt-sheet")).not_to_contain_text(re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}"))  # CPF mascarado


# ----------------------------------------------------------------------
# Cliente
# ----------------------------------------------------------------------
def test_client_portal_and_data_download(page: Page, login):
    login("Cliente")
    expect(page.get_by_role("link", name="OS-2026-00125")).to_be_visible()
    expect(page.get_by_role("heading", name="Privacidade e dados (LGPD)")).to_be_visible()
    with page.expect_download() as download:
        page.get_by_role("button", name=re.compile("Baixar meus dados")).click()
    assert download.value.suggested_filename == "meus-dados-assistencia-tech.json"


def test_client_cannot_open_the_admin_area(page: Page, base_url: str, login):
    login("Cliente")
    page.goto(f"{base_url}/admin")
    expect(page).to_have_url(re.compile(r"/(acesso-negado|minha-conta)"), timeout=20_000)
