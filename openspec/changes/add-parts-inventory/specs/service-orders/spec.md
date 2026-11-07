# Spec Delta

## MODIFIED Requirements

### Requirement: Orçamento com serviços e peças

O sistema SHALL permitir adicionar e remover itens de orçamento do tipo serviço (descrição e valor) e peça (descrição, quantidade inteira positiva e valor unitário) enquanto a ordem estiver Em análise, Aguardando aprovação ou Em reparo. A peça SHALL poder vir do catálogo de estoque, com nome e preço do catálogo, ou ser avulsa. Valores MUST ser positivos, em reais, com no máximo duas casas decimais.

#### Scenario: Inclusão de peça
- **WHEN** o usuário adiciona a peça "SSD 480 GB" com quantidade 1 e valor unitário R$ 250,00
- **THEN** a peça aparece no orçamento com subtotal de R$ 250,00

#### Scenario: Inclusão de peça do catálogo
- **WHEN** o usuário escolhe no catálogo a peça "Fonte 65 W" (R$ 180,00) com quantidade 1
- **THEN** o item aparece com o nome e o preço do catálogo e a peça tem uma unidade a menos em estoque

#### Scenario: Valor inválido
- **WHEN** o usuário adiciona um serviço com valor zero ou negativo
- **THEN** o item não é adicionado e a interface informa que o valor deve ser positivo

#### Scenario: Ordem concluída
- **WHEN** o usuário tenta adicionar um item a uma ordem Concluída
- **THEN** o item não é adicionado porque o orçamento não pode mais ser alterado

#### Scenario: Envio para aprovação sem itens
- **WHEN** o usuário tenta mover para Aguardando aprovação uma ordem com diagnóstico, mas sem itens de orçamento
- **THEN** a alteração é recusada com a mensagem de que o orçamento precisa ter ao menos um item
