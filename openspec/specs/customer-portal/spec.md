# customer-portal Specification

## Purpose
Define a área do cliente no Assistência TECH, onde o cliente autenticado acompanha as próprias ordens de serviço, sem acesso a dados de outros clientes ou a funções administrativas.

## Requirements

### Requirement: Lista das próprias ordens

O portal (`/minha-conta`) SHALL exigir sessão de um usuário Cliente e SHALL listar somente as ordens do cliente associado à conta, da mais recente para a mais antiga, com código, equipamento, status, data da última atualização, total e saldo.

#### Scenario: Cliente com ordens
- **WHEN** um cliente com duas ordens abre o portal
- **THEN** as duas ordens são exibidas e nenhuma ordem de outro cliente aparece

#### Scenario: Cliente sem ordens
- **WHEN** um cliente sem ordens abre o portal
- **THEN** o portal informa que não há ordens de serviço e indica como solicitar atendimento

#### Scenario: Colaborador no portal
- **WHEN** um colaborador abre `/minha-conta`
- **THEN** ele é levado ao painel administrativo

### Requirement: Detalhe da própria ordem

O portal SHALL exibir o detalhe de uma ordem do próprio cliente com status, equipamento, problema relatado, diagnóstico, itens do orçamento, valores, pagamentos e o andamento dos status, sem dados internos como autores e técnicos.

#### Scenario: Ordem própria
- **WHEN** o cliente abre o detalhe de uma de suas ordens
- **THEN** são exibidos o orçamento, os valores e as mudanças de status com data

#### Scenario: Ordem de outro cliente
- **WHEN** o cliente tenta abrir o detalhe de uma ordem de outro cliente pelo endereço
- **THEN** a página informa que a ordem não foi encontrada, sem revelar se ela existe

### Requirement: Dados da conta

O portal SHALL exibir o nome, o e-mail, o CPF mascarado (apenas os dois últimos dígitos visíveis) e o telefone do cliente.

#### Scenario: CPF mascarado
- **WHEN** o cliente com CPF `529.982.247-25` abre o portal
- **THEN** o CPF é exibido como `***.***.***-25`

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

### Requirement: Prazos e garantia no portal

O portal SHALL exibir a previsão de entrega das ordens do cliente e, nas ordens entregues com garantia, a data "Garantia até". Uma ordem em garantia SHALL ser identificada como tal, sem valor a pagar.

#### Scenario: Ordem em andamento
- **WHEN** o cliente abre uma ordem Em reparo com previsão para 20/11/2026
- **THEN** o portal exibe "Previsão de entrega: 20/11/2026"

#### Scenario: Ordem entregue com garantia
- **WHEN** o cliente abre uma ordem entregue em 07/11/2026
- **THEN** o portal exibe "Garantia até 05/02/2027"

### Requirement: Equipamentos do cliente no portal

O portal SHALL permitir que o cliente cadastre equipamentos (tipo, marca, modelo, número de série opcional e observações) e liste os próprios equipamentos. O cliente MUST NOT ver nem cadastrar equipamentos de outro cliente, e um número de série já cadastrado MUST ser recusado.

#### Scenario: Cadastro de equipamento
- **WHEN** a cliente cadastra um Notebook Dell Inspiron no portal
- **THEN** o equipamento aparece em "Meus equipamentos" e pode ser escolhido numa solicitação

#### Scenario: Número de série repetido
- **WHEN** a cliente informa um número de série que já existe
- **THEN** o cadastro é recusado com a mensagem de número de série já cadastrado

### Requirement: Solicitação de atendimento pelo cliente

O portal SHALL permitir que o cliente solicite atendimento para um equipamento próprio, descrevendo o problema e escolhendo a forma de entrega: levar à loja ou coleta por motoboy. Na coleta, o endereço e o período de preferência SHALL ser obrigatórios. Ao escolher levar à loja, o portal SHALL exibir o endereço e o horário configurados da assistência. A solicitação SHALL criar uma ordem no status Solicitado, visível para a equipe.

#### Scenario: Levar à loja
- **WHEN** a cliente solicita atendimento escolhendo "Levar à loja"
- **THEN** a ordem é criada em Solicitado e o portal mostra o endereço da assistência

#### Scenario: Coleta sem endereço
- **WHEN** a cliente escolhe "Coleta por motoboy" e não informa o endereço
- **THEN** a solicitação é recusada com a mensagem para informar o endereço de coleta

#### Scenario: Equipamento de outro cliente
- **WHEN** um cliente tenta solicitar atendimento para um equipamento que não é dele
- **THEN** a solicitação é recusada
