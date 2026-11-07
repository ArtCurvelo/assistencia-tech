# Tasks

## 1. Domínio e permissões

- [ ] 1.1 Criar a permissão `portal.decide_budget` (somente Cliente) e a operação `client_decision` com o evento "Decisão do cliente"; verificar com testes de domínio (aprovar, recusar com e sem motivo, status errado).

## 2. Serviço e dados

- [ ] 2.1 Acrescentar `PortalService.decide_budget` e `PortalRepository.save_client_decision` (demonstração e Xano); verificar com testes de serviço: decisão própria, ordem de outro cliente, colaborador sem permissão.
- [ ] 2.2 Escrever `POST /portal/decisao_orcamento` em XanoScript, validar pelo Developer MCP, acrescentar ao contrato-alvo (29 endpoints) e enviar após simulação e autorização; verificar com `python -m tools.xano_contract_check`.

## 3. Interface

- [ ] 3.1 No detalhe da ordem do portal, exibir o total e os botões Aprovar/Recusar (com motivo) somente em "Aguardando aprovação"; mostrar a decisão no andamento; verificar no navegador nos modos demonstração e Xano.

## 4. Verificação

- [ ] 4.1 Executar `pytest`, `openspec validate add-client-budget-approval --strict` e o roteiro no Xano real (aprovar uma ordem e recusar outra), registrando os resultados neste arquivo.
