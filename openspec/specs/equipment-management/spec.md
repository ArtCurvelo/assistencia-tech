# equipment-management Specification

## Purpose
Define o cadastro dos equipamentos recebidos pela assistência, seu vínculo com os clientes, a manutenção dos dados e a consulta do histórico de manutenções de cada aparelho.

## Requirements

### Requirement: Cadastro de equipamento vinculado ao cliente

O cadastro de equipamento SHALL exigir um cliente existente, o tipo, a marca e o modelo, SHALL aceitar número de série e observações opcionais e SHALL atribuir um identificador único ao equipamento.

#### Scenario: Cadastro completo
- **WHEN** o usuário cadastra um notebook da marca Lenovo, modelo IdeaPad 3, para um cliente existente
- **THEN** o equipamento é criado e aparece na lista com o nome atual do cliente

#### Scenario: Cliente inexistente
- **WHEN** o cadastro referencia um cliente que não existe
- **THEN** nenhum equipamento é criado e a interface informa que o cliente não foi encontrado

### Requirement: Tipos de equipamento

O tipo do equipamento SHALL ser um dos valores Computador, Notebook, Console, Celular, Tablet ou Outro.

#### Scenario: Tipo desconhecido
- **WHEN** o cadastro informa um tipo fora da lista permitida
- **THEN** o cadastro é recusado com a mensagem de que o tipo é inválido

### Requirement: Unicidade do número de série

Quando informado, o número de série MUST ser único entre os equipamentos cadastrados, desconsiderando espaços e diferenças de maiúsculas e minúsculas.

#### Scenario: Número de série repetido
- **WHEN** o usuário cadastra um equipamento com o número de série de outro equipamento
- **THEN** o cadastro é recusado com a mensagem de que o número de série já está cadastrado

#### Scenario: Equipamentos sem número de série
- **WHEN** o usuário cadastra dois equipamentos sem número de série
- **THEN** ambos são criados

### Requirement: Edição de equipamento

O sistema SHALL permitir editar tipo, marca, modelo, número de série e observações de um equipamento, aplicando as mesmas validações do cadastro. O cliente vinculado MUST NOT ser alterado quando o equipamento possuir ordens de serviço.

#### Scenario: Correção do modelo
- **WHEN** o usuário corrige o modelo de um equipamento
- **THEN** o novo modelo aparece na lista e nas ordens de serviço desse equipamento

#### Scenario: Troca de cliente com ordens existentes
- **WHEN** o usuário tenta vincular a outro cliente um equipamento que já possui ordens de serviço
- **THEN** a alteração é recusada e o vínculo original é mantido

### Requirement: Exclusão controlada de equipamento

A exclusão de equipamento SHALL exigir confirmação explícita e MUST ser bloqueada quando o equipamento possuir ordens de serviço.

#### Scenario: Equipamento com ordens
- **WHEN** o usuário tenta excluir um equipamento que possui ordens de serviço
- **THEN** a exclusão é recusada com uma mensagem que informa a existência das ordens

#### Scenario: Equipamento sem ordens
- **WHEN** o usuário confirma a exclusão de um equipamento sem ordens
- **THEN** o equipamento é removido da lista

### Requirement: Pesquisa e filtro de equipamentos

A lista de equipamentos SHALL permitir pesquisa por cliente, marca, modelo ou número de série e filtro por tipo.

#### Scenario: Filtro por tipo
- **WHEN** o usuário filtra a lista pelo tipo Console
- **THEN** somente os equipamentos do tipo Console são exibidos

### Requirement: Histórico de manutenção do equipamento

O sistema SHALL exibir, para cada equipamento, as ordens de serviço associadas a ele, com código, data de abertura, problema relatado e status, da mais recente para a mais antiga.

#### Scenario: Equipamento com reparos anteriores
- **WHEN** o usuário consulta o histórico de um equipamento com uma ordem concluída e outra em reparo
- **THEN** as duas ordens são exibidas com seus status, a mais recente primeiro
