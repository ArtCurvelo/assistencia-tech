"""Verificações estáticas do backend em XanoScript (pasta ``xano/``).

Erros que o validador do Xano aceita, mas que quebram o contrato em execução.
"""

import pathlib
import re

XANO = pathlib.Path(__file__).resolve().parent.parent / "xano"


def _queries():
    return sorted((XANO / "api").rglob("*.xs"))


def test_addon_paths_match_the_return_type():
    # Em lista sem paginação o resultado é um array: o caminho do addon é o próprio campo
    # ("_itens"). O prefixo "items." só existe em resultados paginados; usado numa lista
    # simples, o Xano devolve "items": null e a ordem chega sem itens nem pagamentos.
    problems = []
    for path in _queries():
        text = path.read_text(encoding="utf-8")
        for block in re.findall(r"db\.query[^\n]*\{(.*?)\}\s*as \$", text, flags=re.S):
            paginated = "paging" in block
            uses_items_prefix = 'as: "items.' in block
            if uses_items_prefix and not paginated:
                problems.append(path.relative_to(XANO).as_posix())
    assert problems == []


def test_list_endpoints_with_addons_exist():
    # Garante que a verificação acima de fato cobre as listagens com addons.
    with_addons = [p for p in _queries() if "addon = [" in p.read_text(encoding="utf-8")]
    assert len(with_addons) >= 2
