# privacy Specification

## Purpose
Define os direitos do titular dos dados (LGPD) no portal do Assistência TECH: exportação dos próprios dados e exclusão da conta com anonimização do cadastro, mantendo as ordens.

## Requirements

### Requirement: Exportação dos próprios dados

O portal SHALL permitir que o cliente baixe, em JSON, o próprio cadastro, os equipamentos, as ordens de serviço (itens, pagamentos e andamento) e as avaliações. O arquivo MUST conter apenas dados do próprio cliente e MUST NOT incluir autores internos do histórico.

#### Scenario: Cliente baixa os dados
- **WHEN** a cliente aciona "Baixar meus dados"
- **THEN** recebe o arquivo `meus-dados-assistencia-tech.json` com o cadastro dela e as ordens dela

### Requirement: Exclusão da conta pelo titular

O portal SHALL permitir que o cliente exclua a própria conta, confirmando com a senha. A exclusão SHALL anonimizar nome, CPF, e-mail e telefone do cadastro, desativar o login e apagar os comentários das avaliações, mantendo as ordens e os valores. A exclusão MUST ser recusada com senha incorreta e enquanto houver ordem que não esteja Entregue nem Cancelada.

#### Scenario: Exclusão concluída
- **WHEN** um cliente sem ordens em andamento confirma a exclusão com a senha correta
- **THEN** a sessão é encerrada, o login deixa de funcionar e a equipe passa a ver "Cliente anonimizado" nas ordens dele

#### Scenario: Ordem em andamento
- **WHEN** o cliente tem uma ordem Em reparo e pede a exclusão
- **THEN** o pedido é recusado com a mensagem de que há ordens em andamento

#### Scenario: Senha incorreta
- **WHEN** a senha informada não confere
- **THEN** o pedido é recusado e nada é alterado

### Requirement: Cadastro anonimizado

Cadastros anonimizados SHALL aparecer para a equipe como "Cliente anonimizado", sem CPF, e-mail ou telefone, e MUST NOT impedir a leitura das listas de clientes e ordens.

#### Scenario: Lista de clientes
- **WHEN** a atendente abre a lista de clientes com um cadastro anonimizado
- **THEN** a lista carrega e mostra "Cliente anonimizado" sem dados pessoais
