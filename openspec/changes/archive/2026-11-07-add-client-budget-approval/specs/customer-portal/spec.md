# Spec Delta

## ADDED Requirements

### Requirement: Decisão do orçamento pelo cliente

No detalhe de uma ordem própria em "Aguardando aprovação", o portal SHALL exibir o total e permitir aprovar ou recusar o orçamento. Aprovar SHALL mover a ordem para "Em reparo". Recusar SHALL exigir um motivo e SHALL mover a ordem para "Cancelado", com o motivo registrado.

#### Scenario: Cliente aprova o orçamento
- **WHEN** o cliente aprova o orçamento de uma ordem própria em "Aguardando aprovação"
- **THEN** a ordem passa para "Em reparo"

#### Scenario: Cliente recusa com motivo
- **WHEN** o cliente recusa o orçamento informando um motivo
- **THEN** a ordem passa para "Cancelado" e o motivo fica registrado no cancelamento

#### Scenario: Recusa sem motivo
- **WHEN** o cliente tenta recusar sem informar o motivo
- **THEN** a recusa não é registrada e o portal pede o motivo

### Requirement: Registro e limites da decisão do cliente

Cada decisão do cliente SHALL ser registrada no histórico como "Decisão do cliente", com o cliente como autor, e SHALL aparecer no andamento do portal. A decisão MUST ser recusada para ordens de outros clientes e para ordens fora de "Aguardando aprovação".

#### Scenario: Decisão no histórico
- **WHEN** o cliente aprova ou recusa um orçamento
- **THEN** o histórico registra a decisão com o nome do cliente como autor, e o andamento do portal a exibe

#### Scenario: Ordem fora de aprovação
- **WHEN** o cliente tenta decidir o orçamento de uma ordem que não está em "Aguardando aprovação"
- **THEN** a decisão é recusada e as opções de decisão não são exibidas

#### Scenario: Ordem de outro cliente
- **WHEN** um cliente tenta decidir o orçamento de uma ordem de outro cliente
- **THEN** a ordem é tratada como não encontrada e nada é alterado
