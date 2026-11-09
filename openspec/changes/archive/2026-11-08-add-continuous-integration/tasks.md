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
- **GitHub Actions (2026-11-08/09), repositório `ArtCurvelo/assistencia-tech`:**
  - execução 42518910605 (`84de407`) → falha na coleta: `ModuleNotFoundError: No module named 'greenlet'`. O Reflex importa `sqlalchemy.ext.asyncio`, e no SQLAlchemy 2.1 o `greenlet` é opcional; a `.venv` local o tinha por acaso. OpenSpec passou.
  - correção `2c19a57`: `greenlet>=3.0` no `requirements.txt` e ações `checkout@v5`, `setup-python@v6`, `setup-node@v5` (Node 24); conferida antes num ambiente Python limpo (434 passed, 70%, contrato 35 de 35, 20 páginas).
  - execução 42557605011 (`2c19a57`) → sucesso nos dois jobs, em todos os passos.
