# Proposal: Especificar o comportamento da integração com o Xano

## Why

A mudança `integrate-xano-backend` foi arquivada com requisitos escritos na fase inicial, quando nenhum contrato do Xano existia. O grupo 6 dessa mudança implementou e verificou no workspace 170741 comportamentos que as especificações vigentes não descrevem: a sessão com o token do Xano, as projeções públicas e do portal feitas no servidor, as mensagens das regras do backend, as contas remotas e o limite de requisições do plano gratuito. Esses comportamentos estão apenas no `design.md` arquivado (D12 a D15) e em `docs/XANO_INTEGRATION.md`. Esta mudança os registra como requisitos com cenários, para que a especificação descreva o sistema que de fato funciona.

## What Changes

- Somente especificação: nenhum código é alterado. Cada cenário aponta para os testes que já o verificam.
- Acrescentar à capacidade `backend-integration` os requisitos de sessão com o token do Xano, projeções no servidor, mensagens das pré-condições, contas remotas, limite de requisições e conferência do contrato publicado.
- Ajustar o requisito "Tradução das respostas de erro" para distinguir sessão inválida (401) de falta de permissão (403) e para indisponibilidade não encerrar a sessão.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `backend-integration`: novos requisitos e ajuste da tradução de erros.

## Impact

- **Código:** nenhum.
- **Especificação:** `openspec/specs/backend-integration/spec.md` ao arquivar.
- **Verificação:** testes existentes (`tests/test_xano.py`, `tests/test_xano_repositories.py`, `tests/test_xano_contract_check.py`, `tests/test_xanoscript_static.py`) e o registro da tarefa 6.5 da mudança arquivada.

## Out of Scope

- Qualquer mudança de comportamento, de código ou do backend em XanoScript.
