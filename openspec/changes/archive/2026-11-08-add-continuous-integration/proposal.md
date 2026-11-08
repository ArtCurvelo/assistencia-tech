# Proposal: Integração contínua no GitHub

## Why

Os testes, a validação das especificações e a conferência do contrato com o Xano só rodam quando alguém lembra de executá-los no próprio computador. Uma alteração pode chegar ao repositório quebrando regras já testadas, e o professor não tem como ver que o projeto passa nas verificações sem instalar tudo. Com integração contínua, cada envio ao GitHub roda as mesmas verificações num ambiente limpo e o resultado fica público no repositório.

## What Changes

- **Workflow do GitHub Actions** (`.github/workflows/ci.yml`), disparado em todo `push` e `pull_request`:
  - **Testes:** instala as dependências de `requirements-dev.txt` em Python 3.14, roda `pytest` com cobertura e o verificador de contrato com as cópias da documentação do Xano (`--offline`) e confirma que o aplicativo Reflex monta todas as páginas.
  - **Especificações:** roda `openspec validate --all --strict`.
- **Regras do projeto como testes:** arquivos Python com menos de 1.000 linhas, nenhum `.env` versionado e nenhum token JWT nos arquivos versionados.
- **Sem segredos:** o workflow não usa credenciais nem acessa o Xano real; tudo roda sobre o modo demonstração e servidores simulados.
- README com a seção de integração contínua e a versão de Python testada.

## Capabilities

### New Capabilities

- `continuous-integration`: verificações automáticas a cada envio ao repositório.

### Modified Capabilities

- Nenhuma.

## Impact

- **Arquivos:** `.github/workflows/ci.yml`, `tests/test_project_rules.py`, README.
- **Execução:** depende de o repositório estar no GitHub (ainda não há repositório remoto configurado).

## Out of Scope

- Publicação automática do site (incremento de deploy).
- Testes de ponta a ponta no navegador dentro do workflow.
- Testes contra o Xano real (exigiriam credenciais no GitHub).
