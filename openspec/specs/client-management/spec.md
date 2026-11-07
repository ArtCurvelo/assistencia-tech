# client-management Specification

## Purpose
Define o cadastro e a manutenção dos clientes da assistência técnica, incluindo validação de documentos e contatos, edição, exclusão controlada e consulta do histórico de atendimentos.

## Requirements

### Requirement: Dados obrigatórios do cliente

O cadastro de cliente SHALL exigir nome, CPF, e-mail e telefone, e SHALL atribuir a cada cliente um identificador único que não muda ao longo do tempo.

#### Scenario: Cadastro completo
- **WHEN** o usuário cadastra um cliente com nome, CPF válido, e-mail válido e telefone válido
- **THEN** o cliente é criado com um identificador único e passa a aparecer na lista de clientes

#### Scenario: Campo obrigatório ausente
- **WHEN** o usuário envia o cadastro sem o CPF
- **THEN** nenhum cliente é criado e a interface informa que o CPF é obrigatório

### Requirement: Validação de CPF

O sistema SHALL aceitar o CPF com ou sem pontuação, SHALL validá-lo pelos dígitos verificadores, SHALL rejeitar sequências de dígitos repetidos e SHALL exibi-lo no formato `000.000.000-00`.

#### Scenario: CPF com dígito verificador incorreto
- **WHEN** o usuário informa o CPF `123.456.789-00`
- **THEN** o cadastro é recusado com a mensagem de que o CPF é inválido

#### Scenario: CPF sem pontuação
- **WHEN** o usuário informa o CPF válido `52998224725`
- **THEN** o cliente é salvo e o CPF é exibido como `529.982.247-25`

#### Scenario: Dígitos repetidos
- **WHEN** o usuário informa o CPF `111.111.111-11`
- **THEN** o cadastro é recusado com a mensagem de que o CPF é inválido

### Requirement: Validação de telefone

O sistema SHALL aceitar telefones brasileiros com DDD, fixos (10 dígitos) ou celulares (11 dígitos, iniciando por 9 após o DDD), com ou sem pontuação, e SHALL exibi-los no formato `(00) 00000-0000` ou `(00) 0000-0000`.

#### Scenario: Celular válido sem pontuação
- **WHEN** o usuário informa o telefone `11987654321`
- **THEN** o telefone é salvo e exibido como `(11) 98765-4321`

#### Scenario: Telefone com quantidade inválida de dígitos
- **WHEN** o usuário informa o telefone `98765-432`
- **THEN** o cadastro é recusado com a mensagem de que o telefone é inválido

### Requirement: Unicidade de CPF e e-mail

O sistema MUST NOT permitir dois clientes com o mesmo CPF ou com o mesmo e-mail, desconsiderando pontuação do CPF e diferenças de maiúsculas e minúsculas do e-mail.

#### Scenario: CPF já cadastrado
- **WHEN** o usuário cadastra um cliente com um CPF já pertencente a outro cliente
- **THEN** o cadastro é recusado com a mensagem de que o CPF já está cadastrado

### Requirement: Edição de cliente

O sistema SHALL permitir editar nome, CPF, e-mail e telefone de um cliente, aplicando as mesmas validações e regras de unicidade do cadastro, e SHALL preservar os vínculos com equipamentos e ordens existentes.

#### Scenario: Alteração do nome
- **WHEN** o usuário altera o nome de um cliente que possui ordens de serviço
- **THEN** o novo nome passa a aparecer na lista de clientes e nas ordens desse cliente

#### Scenario: Edição com e-mail de outro cliente
- **WHEN** o usuário altera o e-mail de um cliente para o e-mail de outro cliente
- **THEN** a alteração é recusada e os dados anteriores são mantidos

### Requirement: Exclusão controlada de cliente

A exclusão de cliente SHALL exigir confirmação explícita do usuário e MUST ser bloqueada quando o cliente possuir equipamentos ou ordens de serviço vinculados.

#### Scenario: Cliente sem vínculos
- **WHEN** o usuário confirma a exclusão de um cliente sem equipamentos nem ordens
- **THEN** o cliente é removido da lista

#### Scenario: Cliente com vínculos
- **WHEN** o usuário tenta excluir um cliente que possui equipamentos ou ordens
- **THEN** a exclusão é recusada com uma mensagem que informa os vínculos existentes

#### Scenario: Exclusão cancelada
- **WHEN** o usuário inicia a exclusão e cancela a confirmação
- **THEN** o cliente permanece cadastrado

### Requirement: Pesquisa de clientes

A lista de clientes SHALL permitir pesquisa por nome, e-mail, CPF ou telefone, desconsiderando maiúsculas, minúsculas e pontuação de CPF e telefone.

#### Scenario: Pesquisa por CPF sem pontuação
- **WHEN** o usuário pesquisa `52998224725`
- **THEN** a lista exibe o cliente com o CPF `529.982.247-25`

### Requirement: Histórico de atendimentos do cliente

O sistema SHALL oferecer uma página de detalhe do cliente com seus dados, seus equipamentos e suas ordens de serviço, ordenadas da mais recente para a mais antiga, com código, equipamento, status e data de abertura.

#### Scenario: Consulta do histórico
- **WHEN** o usuário abre o detalhe de um cliente com duas ordens de serviço
- **THEN** a página exibe as duas ordens, da mais recente para a mais antiga, com acesso ao detalhe de cada uma

#### Scenario: Cliente inexistente
- **WHEN** o usuário acessa o detalhe de um identificador de cliente que não existe
- **THEN** a página informa que o cliente não foi encontrado e oferece retorno à lista
