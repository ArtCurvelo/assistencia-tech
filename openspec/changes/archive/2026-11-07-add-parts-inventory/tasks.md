# Tasks

## 1. Domínio, modelos e permissões

- [x] 1.1 Criar `Part`, `PartCreate` e `StockMovement`, `part_id` em `OrderItem`, as permissões `stock.view`/`stock.manage` e `domain/inventory.py` (situação, disponibilidade e `stock_effects`); verificar com testes de domínio.

## 2. Serviço e modo demonstração

- [x] 2.1 Criar `PartRepository` e `InventoryService` (catálogo, entrada, movimentações, alerta) e a inclusão de peça do catálogo em `OrderService.add_item`; verificar com testes de serviço.
- [x] 2.2 No modo demonstração, aplicar `stock_effects` ao gravar ordens (inclusão, remoção, cancelamento e recusa do cliente) e semear peças; verificar com testes.

## 3. Backend Xano

- [x] 3.1 Criar as tabelas `peca` e `movimento_estoque`, `peca_id` em `os_itens`, os endpoints de catálogo, entrada e movimentações, e as regras de estoque em `os_itens`, `os_servicos` (cancelamento) e `portal/decisao_orcamento`; validar pelo Developer MCP e simular o envio.
- [x] 3.2 Acrescentar os endpoints ao contrato-alvo, enviar após autorização e confirmar com `python -m tools.xano_contract_check`.
- [x] 3.3 Implementar o adaptador Xano (`PartRepository`, `peca_id` nos itens); verificar com testes sobre servidor simulado.

## 4. Interface

- [x] 4.1 Página `/admin/estoque` (catálogo, cadastro, edição, entrada, situação e movimentações), item "Estoque" no menu e peça do catálogo no formulário do orçamento; alerta de estoque baixo no painel; verificar no navegador.

## 5. Verificação

- [x] 5.1 Executar `pytest`, `openspec validate add-parts-inventory --strict` e o roteiro no Xano real (cadastro, entrada, baixa, insuficiência, devolução por remoção e por cancelamento), registrando os resultados.

## Registro de verificação (2026-11-07)

- **pytest (.venv):** 394 passed in 79.10s (0:01:19) (14 testes novos em `tests/test_parts_inventory.py`; matriz de permissões atualizada).
- **OpenSpec:** `openspec validate add-parts-inventory --strict` válido.
- **XanoScript:** 58 arquivos válidos no Developer MCP; envio após simulação e autorização; verificador: 34 de 34.
- **Regras no Xano real** (API, contas de teste da atendente e do técnico):
  - cadastro com quantidade 0; código repetido → "Já existe uma peça com este código."; técnico repondo → 403;
  - entrada de 3 → 3; ordem OS-2026-00004 aberta e em análise; incluir 5 → "Estoque insuficiente para a peça escolhida.";
  - incluir 2 → estoque 1; remover o item → 3; incluir 3 → 0; cancelar a ordem → 3;
  - movimentações: entrada, saída, devolução (remoção) e devolução (cancelamento), com autor e a ordem relacionada.
- **Navegador:**
  - modo demonstração: página com situações (Normal, Baixo, Esgotado), entrada (Esgotado → Normal), alerta do painel (2 → 1), peça do catálogo no orçamento (descrição e preço do catálogo, "disp." atualizado) e recusa por estoque insuficiente com a quantidade disponível;
  - Xano real (atendente de teste): página com as peças e movimentações do servidor, código da ordem nas saídas e devoluções, cadastro de "SSD-480" (Esgotado e alerta) e entrada de 6 (Normal).
- **Registros de teste no Xano:** peça TST-82140, peça SSD-480 e ordem OS-2026-00004 (cancelada).
- **Ajuste após arquivar:** `openspec validate --all --strict` apontou o "Purpose" provisório de `inventory` e o requisito "Matriz de permissões" de `access-control` com mais de 500 caracteres. O Purpose foi escrito e as regras de estoque passaram ao requisito próprio "Permissões de estoque", com o mesmo conteúdo e o cenário do técnico.
