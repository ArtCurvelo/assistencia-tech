# Proposal: Estoque de peças

## Why

Hoje cada peça do orçamento é digitada à mão (descrição e valor), sem relação com o que a assistência tem em estoque. Não há como saber quantas unidades de uma peça existem, se uma peça orçada está disponível, quanto foi consumido nem quando é hora de repor. Isso gera orçamentos com peças em falta, preços inconsistentes entre ordens e nenhuma rastreabilidade do material. Um catálogo de peças com controle de estoque liga o orçamento ao inventário real, evita prometer peças que não existem e dá ao administrador a informação para repor no momento certo.

## What Changes

- Catálogo de peças com código único, nome, preço de venda, quantidade em estoque, estoque mínimo e situação (ativa ou inativa).
- Entrada de estoque (reposição) com quantidade e observação.
- Movimentações de estoque registradas (entrada, saída por ordem de serviço, devolução), com data, autor e ordem relacionada.
- No orçamento, uma peça pode vir do catálogo: descrição e preço vêm do catálogo e a quantidade sai do estoque na inclusão. A remoção do item ou o cancelamento da ordem (inclusive a recusa pelo cliente) devolvem as unidades ao estoque. A peça avulsa (fora do estoque) continua possível.
- Uma peça sem estoque suficiente não pode ser incluída no orçamento.
- Situação do estoque por peça (normal, baixo, esgotado) e alerta de estoque baixo no painel.
- Nova página "Estoque" no painel administrativo.
- Backend Xano: tabelas `peca` e `movimento_estoque`, campo `peca_id` em `os_itens`, endpoints de catálogo, entrada e movimentações; as regras de estoque ficam no servidor, em transações.

## Capabilities

### New Capabilities

- `inventory`: catálogo de peças, entrada, movimentações, situação do estoque e consumo pelas ordens de serviço.

### Modified Capabilities

- `service-orders`: o orçamento passa a aceitar peças do catálogo, com baixa e devolução de estoque.
- `access-control`: a matriz de permissões inclui consultar e gerenciar o estoque.

## Impact

- **Código:** `models` (peça e movimentação; `part_id` no item), `domain/inventory.py`, `services/inventory.py`, `OrderService.add_item`, `data/repositories.py` (`PartRepository`), modo demonstração, adaptador Xano, estado e página de estoque, formulário de itens, painel.
- **Backend:** novas tabelas e endpoints em `xano/`; alterações em `os_itens` (POST/DELETE), `os_servicos` (PATCH) e `portal/decisao_orcamento`.
- **Testes:** domínio, serviço sobre a demonstração, adaptador Xano simulado, verificador de contrato.

## Out of Scope

- Fornecedores, pedidos de compra e custo médio.
- Inventário físico (contagem) e ajustes manuais de saída.
- Reserva de peças sem inclusão no orçamento.
