# Tasks

## 1. Domínio, modelos e permissões

- [x] 1.1 Criar `Part`, `PartCreate` e `StockMovement`, `part_id` em `OrderItem`, as permissões `stock.view`/`stock.manage` e `domain/inventory.py` (situação, disponibilidade e `stock_effects`); verificar com testes de domínio.

## 2. Serviço e modo demonstração

- [x] 2.1 Criar `PartRepository` e `InventoryService` (catálogo, entrada, movimentações, alerta) e a inclusão de peça do catálogo em `OrderService.add_item`; verificar com testes de serviço.
- [x] 2.2 No modo demonstração, aplicar `stock_effects` ao gravar ordens (inclusão, remoção, cancelamento e recusa do cliente) e semear peças; verificar com testes.

## 3. Backend Xano

- [x] 3.1 Criar as tabelas `peca` e `movimento_estoque`, `peca_id` em `os_itens`, os endpoints de catálogo, entrada e movimentações, e as regras de estoque em `os_itens`, `os_servicos` (cancelamento) e `portal/decisao_orcamento`; validar pelo Developer MCP e simular o envio.
- [ ] 3.2 Acrescentar os endpoints ao contrato-alvo, enviar após autorização e confirmar com `python -m tools.xano_contract_check`.
- [x] 3.3 Implementar o adaptador Xano (`PartRepository`, `peca_id` nos itens); verificar com testes sobre servidor simulado.

## 4. Interface

- [ ] 4.1 Página `/admin/estoque` (catálogo, cadastro, edição, entrada, situação e movimentações), item "Estoque" no menu e peça do catálogo no formulário do orçamento; alerta de estoque baixo no painel; verificar no navegador.

## 5. Verificação

- [ ] 5.1 Executar `pytest`, `openspec validate add-parts-inventory --strict` e o roteiro no Xano real (cadastro, entrada, baixa, insuficiência, devolução por remoção e por cancelamento), registrando os resultados.
