# Tasks

## 1. Domínio e permissões

- [x] 1.1 Criar a permissão `portal.decide_budget` (somente Cliente) e a operação `client_decision` com o evento "Decisão do cliente"; verificar com testes de domínio (aprovar, recusar com e sem motivo, status errado).

## 2. Serviço e dados

- [x] 2.1 Acrescentar `PortalService.decide_budget` e `PortalRepository.save_client_decision` (demonstração e Xano); verificar com testes de serviço: decisão própria, ordem de outro cliente, colaborador sem permissão.
- [x] 2.2 Escrever `POST /portal/decisao_orcamento` em XanoScript, validar pelo Developer MCP, acrescentar ao contrato-alvo (29 endpoints) e enviar após simulação e autorização; verificar com `python -m tools.xano_contract_check`.

## 3. Interface

- [x] 3.1 No detalhe da ordem do portal, exibir o total e os botões Aprovar/Recusar (com motivo) somente em "Aguardando aprovação"; mostrar a decisão no andamento; verificar no navegador nos modos demonstração e Xano.

## 4. Verificação

- [x] 4.1 Executar `pytest`, `openspec validate add-client-budget-approval --strict` e o roteiro no Xano real (aprovar uma ordem e recusar outra), registrando os resultados neste arquivo.

## Registro de verificação (2026-11-07)

- **pytest (.venv):** 372 passed in 59.65s (11 testes novos em `tests/test_client_budget_approval.py`; matriz de permissões atualizada).
- **OpenSpec:** `openspec validate add-client-budget-approval --strict` válido.
- **XanoScript:** 47 arquivos válidos no Developer MCP; `POST /portal/decisao_orcamento` enviado após simulação e autorização; verificador: 29 de 29.
- **Endpoint no Xano real (token da cliente de teste):** ordem Entregue → 400 "Esta ordem não está aguardando a sua aprovação."; ordem inexistente → 404; sem token → 401.
- **Navegador, Xano real** (administrador no Chrome; cliente de teste no navegador do app):
  - OS-2026-00002 e OS-2026-00003 levadas a "Aguardando aprovação" pelo administrador.
  - Portal: painel "Orçamento aguardando a sua aprovação" com total (R$ 220,00) e os botões Aprovar/Recusar.
  - Aprovar OS-2026-00002 → "Em reparo"; painel some; andamento com "Orçamento aprovado pelo cliente.".
  - Recusar OS-2026-00003 sem motivo → "Informe o motivo da recusa."; com motivo → "Cancelado", motivo no cancelamento e no andamento.
  - Painel do administrador: histórico com "Decisão do cliente" e mudança de status de autoria "Joana Teixeira (Cliente)".
- **Observação (anterior a esta mudança):** ordens canceladas exibem o saldo do orçamento como "Saldo devedor", embora o pagamento apareça como "Não se aplica".
