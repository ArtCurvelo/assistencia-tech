# Design: Estoque de peças

## Context

O item de orçamento (`OrderItem`) tem tipo, descrição, quantidade e valor unitário, sem vínculo com cadastro de peças. A ordem é um agregado salvo por diferença (D13 de `integrate-xano-backend`): itens novos viram `POST /os_itens`, itens removidos `DELETE /os_itens/{id}`, e a mudança de status `PATCH /os_servicos/{id}`. O cancelamento pode vir de um colaborador ou da recusa do cliente no portal (`POST /portal/decisao_orcamento`).

## Decisions

### D1. Peça do catálogo como vínculo opcional do item

`OrderItem` ganha `part_id` (vazio para peça avulsa e para serviço). Com peça do catálogo, o serviço de ordens usa o nome e o preço do catálogo, força o tipo "Peça" e confere se a peça está ativa e com quantidade suficiente, para dar uma mensagem clara antes de gravar.

### D2. O estoque acompanha os itens na camada de dados

A quantidade em estoque é mantida pela camada de persistência, como um gatilho de banco: incluir um item com peça dá baixa, remover devolve, e cancelar a ordem devolve todas as peças ainda no orçamento. A regra que calcula esses efeitos é uma função pura (`domain.inventory.stock_effects(antes, depois)`), usada pelo modo demonstração. No Xano, os mesmos efeitos acontecem nos endpoints, em transação com a gravação do item ou do status, e o servidor recusa quantidade negativa. Assim a recusa do cliente (perfil sem acesso ao estoque) também devolve as peças, sem permissão extra.

### D3. Movimentações imutáveis

Cada efeito gera uma movimentação (`Entrada`, `Saída`, `Devolução`) com quantidade, data, autor e ordem relacionada. Movimentações não são editadas nem excluídas; a quantidade da peça é o saldo resultante.

### D4. Situação do estoque

`Esgotado` (quantidade 0), `Baixo` (quantidade ≤ estoque mínimo) ou `Normal`. O painel conta as peças ativas em `Baixo` ou `Esgotado`.

### D5. Mesmo grupo de API das ordens

Os endpoints de estoque ficam no grupo `assistencia-tech-os`, que já trata do orçamento, sem nova configuração de grupo.

### D6. Evento de carga próprio da página de estoque

Verificado no navegador: com `on_load=InventoryState.load_admin_data` (herdado de `AdminState`), o Reflex executou o `_reload` de `AdminState`, e não a sobrescrita de `InventoryState`; a página mostrava o alerta, mas a tabela vazia. A página usa um evento próprio, `InventoryState.load_inventory`, que chama a verificação de acesso e a carga do estoque.

## Risks / Trade-offs

- [Baixa no orçamento, antes da aprovação] → a peça fica separada para a ordem enquanto o cliente decide; a recusa e o cancelamento devolvem as unidades automaticamente.
- [Corrida por última unidade] → o servidor confere a quantidade dentro da transação; o segundo pedido recebe "Estoque insuficiente".
- [Limite de requisições do Xano] → a página de estoque faz duas leituras (peças e movimentações) e o painel uma a mais (peças).
