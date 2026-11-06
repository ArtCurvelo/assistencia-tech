# Spec Delta

## Purpose

Define como o Assistência TECH escolhe e utiliza sua fonte de dados, garantindo que o modo demonstração seja sempre identificável e que falhas de acesso a dados sejam comunicadas ao usuário de forma compreensível.

## ADDED Requirements

### Requirement: Seleção da fonte de dados por configuração

O sistema SHALL determinar a fonte de dados ativa (demonstração ou Xano) a partir da configuração do ambiente, sem exigir alteração de código. Na ausência de configuração, o sistema SHALL usar o modo demonstração.

#### Scenario: Ambiente sem configuração
- **WHEN** a aplicação é iniciada sem nenhuma variável de fonte de dados definida
- **THEN** o sistema opera no modo demonstração

#### Scenario: Fonte de dados desconhecida
- **WHEN** a configuração indica uma fonte de dados que o sistema não reconhece
- **THEN** a inicialização da camada de dados falha com uma mensagem que identifica o valor inválido e as opções aceitas

### Requirement: Sem substituição silenciosa de dados reais

Quando a fonte Xano estiver configurada, o sistema MUST NOT recorrer automaticamente aos dados de demonstração em caso de configuração incompleta ou falha de comunicação.

#### Scenario: Xano selecionado sem endereço configurado
- **WHEN** a fonte Xano é selecionada e o endereço base da API não está configurado
- **THEN** o sistema informa que a configuração está incompleta e não exibe dados de demonstração no lugar dos dados reais

### Requirement: Identificação da fonte ativa

A interface administrativa SHALL exibir qual fonte de dados está ativa, e o modo demonstração SHALL ser identificado como tal em todas as páginas administrativas.

#### Scenario: Navegação no modo demonstração
- **WHEN** o usuário acessa qualquer página administrativa no modo demonstração
- **THEN** a interface indica que os dados exibidos são demonstrativos

### Requirement: Operações de dados no modo demonstração

O modo demonstração SHALL oferecer consulta e cadastro de clientes, equipamentos e ordens de serviço, além da atualização de status das ordens, mantendo os dados apenas durante a execução da aplicação.

#### Scenario: Cadastro de cliente no modo demonstração
- **WHEN** o usuário cadastra um cliente com nome e e-mail válidos
- **THEN** o cliente passa a aparecer na lista de clientes

#### Scenario: Status inválido
- **WHEN** uma atualização tenta atribuir a uma ordem um status fora do conjunto de status permitidos
- **THEN** a ordem mantém o status anterior e o usuário é informado de que o status é inválido

### Requirement: Código único e padronizado da ordem de serviço

Toda ordem de serviço criada SHALL receber um código único no formato `OS-AAAA-NNNNN`, em que `AAAA` é o ano e `NNNNN` é um número sequencial com cinco dígitos.

#### Scenario: Criação de nova ordem
- **WHEN** uma ordem é criada após a ordem `OS-2026-00125`
- **THEN** a nova ordem recebe o código `OS-2026-00126`

### Requirement: Comunicação de falhas de acesso a dados

Quando uma operação de dados falhar, a interface SHALL apresentar uma mensagem compreensível ao usuário, sem expor detalhes técnicos como endereços, credenciais ou rastros de execução, e SHALL preservar os dados já exibidos.

#### Scenario: Backend indisponível
- **WHEN** uma operação não consegue se comunicar com o backend
- **THEN** a interface informa que o serviço está indisponível e sugere tentar novamente

#### Scenario: Formulário com dados obrigatórios ausentes
- **WHEN** o usuário envia um formulário administrativo sem preencher um campo obrigatório
- **THEN** a interface informa qual informação está faltando e nenhum registro é criado

### Requirement: Indicação de operação em andamento

A interface SHALL indicar quando uma operação de dados está em andamento e impedir o envio duplicado do mesmo formulário durante esse período.

#### Scenario: Envio de formulário
- **WHEN** o usuário envia um formulário de cadastro
- **THEN** o botão de envio indica carregamento até a operação terminar com sucesso ou erro
