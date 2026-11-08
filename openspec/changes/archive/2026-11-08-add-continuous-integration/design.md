# Design: Integração contínua no GitHub

## Decisions

### D1. Dois jobs independentes

`testes` (Python) e `especificacoes` (Node com o OpenSpec) rodam em paralelo; um não esconde a falha do outro. Ambos em `ubuntu-latest`, com `permissions: contents: read` (o workflow só lê o repositório) e `concurrency` que cancela execuções antigas do mesmo ramo.

### D2. Python 3.14, a versão da `.venv`

O projeto só foi testado com Python 3.14 (a `.venv` local). O workflow usa a mesma versão para que o resultado no GitHub signifique o mesmo que o resultado local. Outras versões ficam fora até serem testadas; o README passa a dizer "testado com Python 3.14" em vez de "3.10+" (o código usa `StrEnum`, que não existe no 3.10).

### D3. Nenhum segredo, nenhum acesso externo além dos pacotes

Os testes usam o modo demonstração e `httpx.MockTransport`; o verificador de contrato roda com `--offline` sobre `docs/xano-openapi/`. O workflow não define `secrets` e não contata o Xano.

### D4. Montagem do aplicativo como teste de fumaça

`python -c "import assistencia_tech.assistencia_tech"` monta todas as páginas e rotas do Reflex sem iniciar o servidor nem instalar o frontend em Node; pega erros de componentes e de estado que os testes unitários não cobrem.

### D5. Regras do projeto como testes

`tests/test_project_rules.py` transforma em teste as regras do prompt do projeto que podem ser conferidas automaticamente: menos de 1.000 linhas por arquivo Python; nenhum `.env` versionado; nenhum token JWT (`eyJ….eyJ…`) nos arquivos versionados. A lista de arquivos vem de `git ls-files`, a mesma no computador e no GitHub.

### D6. Versão fixa do OpenSpec

`npx @fission-ai/openspec@1.14.3` (a versão local) evita que uma versão nova do validador quebre o workflow sem mudança no projeto.

## Risks / Trade-offs

- [Python 3.14 indisponível no GitHub] → `actions/setup-python` oferece 3.14; se faltar, o workflow falha de forma visível, sem passar em silêncio.
- [Instalação do Reflex lenta] → cache do `pip` por `requirements*.txt`.
