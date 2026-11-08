# Tasks

## 1. Regras do projeto

- [x] 1.1 Criar `tests/test_project_rules.py` (limite de linhas, `.env` e tokens JWT); verificar que passa no projeto atual e que falha com um caso de exemplo.

## 2. Workflow

- [x] 2.1 Criar `.github/workflows/ci.yml` com os jobs de testes e de especificações, sem segredos, e atualizar o README.

## 3. Verificação

- [x] 3.1 Executar localmente os mesmos comandos do workflow e validar o YAML; registrar os resultados. A primeira execução no GitHub depende de o repositório ser publicado.

## Registro de verificação (2026-11-08)

Comandos do workflow executados localmente (Windows, `.venv` com Python 3.14.7, `ASSISTENCIA_DATA_SOURCE=demo`):

- `python -m pytest --cov=assistencia_tech --cov-report=term-missing:skip-covered` → 435 passed, cobertura total de 70%.
- `tests/test_project_rules.py` → 4 passed, inclusive com o próprio arquivo rastreado pelo git (o token de exemplo é montado por partes) e com casos de exemplo que provam que as regras detectam arquivo grande e token.
- `python -m tools.xano_contract_check --offline` → 35 de 35 endpoints.
- Montagem do aplicativo → 20 páginas.
- `npx --yes @fission-ai/openspec@1.14.3 validate --all --strict --no-interactive` → 17 passed, 0 failed.
- YAML do workflow lido com PyYAML (instalado só para a conferência e removido em seguida): jobs `testes` e `especificacoes` com os passos esperados.
- **Pendente:** a primeira execução no GitHub (Ubuntu) depende de o repositório ser publicado; ainda não há repositório remoto configurado.
