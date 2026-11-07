# inventory Specification

## Purpose
Define o estoque de peças do Assistência TECH: catálogo, entradas, movimentações, situação do estoque e o consumo de peças pelos orçamentos das ordens de serviço, com baixa na inclusão e devolução na remoção ou no cancelamento.

## Requirements

### Requirement: Catálogo de peças

O sistema SHALL manter um catálogo de peças com código único, nome, preço de venda positivo, quantidade em estoque, estoque mínimo e situação ativa ou inativa. Administrador e Atendente SHALL cadastrar e editar peças; colaboradores SHALL consultar o catálogo. A quantidade MUST NOT ser editada diretamente: ela muda apenas por movimentações.

#### Scenario: Cadastro de peça
- **WHEN** o atendente cadastra a peça "SSD 480 GB" com código "SSD-480", preço R$ 250,00 e estoque mínimo 2
- **THEN** a peça aparece no catálogo com quantidade 0 e situação "Esgotado"

#### Scenario: Código repetido
- **WHEN** alguém cadastra uma peça com um código já usado
- **THEN** o cadastro é recusado com a mensagem de que o código já existe

### Requirement: Entrada de estoque

Administrador e Atendente SHALL registrar entradas de estoque com quantidade inteira positiva e observação opcional. Cada entrada SHALL aumentar a quantidade da peça e SHALL ser registrada como movimentação.

#### Scenario: Reposição
- **WHEN** o atendente registra a entrada de 5 unidades de uma peça com 1 unidade
- **THEN** a peça passa a ter 6 unidades e a movimentação "Entrada" fica registrada com autor e data

### Requirement: Movimentações de estoque

Toda alteração de quantidade SHALL gerar uma movimentação imutável do tipo Entrada, Saída ou Devolução, com quantidade, data, autor e, quando houver, a ordem de serviço relacionada. A página de estoque SHALL exibir as movimentações mais recentes.

#### Scenario: Histórico de movimentações
- **WHEN** uma peça recebe uma entrada e depois é usada em uma ordem
- **THEN** as duas movimentações aparecem com tipo, quantidade, autor, data e o código da ordem na saída

### Requirement: Situação do estoque

Cada peça SHALL ter a situação "Esgotado" quando a quantidade for zero, "Baixo" quando for menor ou igual ao estoque mínimo e "Normal" nos demais casos. O painel administrativo SHALL exibir quantas peças ativas estão com estoque baixo ou esgotado.

#### Scenario: Estoque baixo no painel
- **WHEN** uma peça ativa com estoque mínimo 2 fica com 1 unidade
- **THEN** a peça aparece como "Baixo" e é contada no alerta do painel

### Requirement: Consumo de peças pelas ordens

Ao incluir no orçamento uma peça do catálogo, a quantidade SHALL sair do estoque; ao remover o item ou cancelar a ordem, inclusive pela recusa do cliente, as unidades SHALL voltar ao estoque. Uma peça inativa ou sem quantidade suficiente MUST NOT ser incluída. Peças avulsas (fora do catálogo) MUST NOT alterar o estoque.

#### Scenario: Baixa na inclusão
- **WHEN** o técnico inclui 2 unidades de uma peça com 5 em estoque
- **THEN** o item usa o nome e o preço do catálogo, e a peça fica com 3 unidades e uma movimentação de saída para a ordem

#### Scenario: Estoque insuficiente
- **WHEN** o técnico tenta incluir 3 unidades de uma peça com 2 em estoque
- **THEN** o item não é incluído e a mensagem informa a quantidade disponível

#### Scenario: Devolução na remoção
- **WHEN** um item com peça do catálogo é removido do orçamento
- **THEN** as unidades voltam ao estoque com uma movimentação de devolução

#### Scenario: Devolução no cancelamento
- **WHEN** a ordem é cancelada, por um colaborador ou pela recusa do cliente
- **THEN** todas as peças do catálogo ainda no orçamento voltam ao estoque
