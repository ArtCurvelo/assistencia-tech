# Spec Delta

## Purpose

Define como o administrador mantém as contas dos colaboradores da assistência — cadastro, cargo, especialidade, senha provisória e ativação de acesso — preservando sempre a possibilidade de administrar o sistema.

## ADDED Requirements

### Requirement: Acesso exclusivo do administrador

A gestão de colaboradores SHALL estar disponível somente para usuários Administrador; os demais perfis SHALL ver a página de acesso negado e ter as operações recusadas.

#### Scenario: Atendente abre a página
- **WHEN** um atendente abre `/admin/colaboradores`
- **THEN** ele é levado à página de acesso negado

### Requirement: Lista de colaboradores

O sistema SHALL listar os colaboradores (Administrador, Atendente e Técnico) com nome, e-mail, cargo, especialidade quando técnico e situação Ativo ou Inativo, sem exibir contas de clientes.

#### Scenario: Lista inicial
- **WHEN** o administrador abre a página de colaboradores
- **THEN** são exibidos os colaboradores com cargo e situação, e nenhuma conta de cliente aparece

### Requirement: Cadastro de colaborador

O cadastro SHALL exigir nome, e-mail, cargo e senha provisória que atenda à política de senha; o e-mail MUST ser único entre todas as contas. Para o cargo Técnico, SHALL ser informada a especialidade, e o técnico SHALL passar a estar disponível para atribuição nas ordens.

#### Scenario: Novo técnico
- **WHEN** o administrador cadastra "Bruno Alves", cargo Técnico, especialidade "Impressoras", com senha provisória válida
- **THEN** a conta é criada, Bruno consegue entrar com a senha provisória e aparece entre os técnicos disponíveis na ordem de serviço

#### Scenario: E-mail em uso
- **WHEN** o administrador cadastra um colaborador com o e-mail de outra conta
- **THEN** o cadastro é recusado com a mensagem de que o e-mail já está cadastrado

### Requirement: Edição de cargo e dados

O administrador SHALL poder alterar nome, cargo e especialidade de um colaborador. Um técnico com ordens em aberto (de Recebido a Concluído) MUST NOT deixar o cargo Técnico.

#### Scenario: Técnico com ordens em aberto
- **WHEN** o administrador tenta mudar para Atendente o cargo de um técnico responsável por uma ordem Em reparo
- **THEN** a alteração é recusada com a mensagem que informa as ordens em aberto

#### Scenario: Promoção a administrador
- **WHEN** o administrador muda o cargo de um atendente para Administrador
- **THEN** o novo cargo passa a valer a partir da próxima ação desse usuário

### Requirement: Desativação e reativação

O administrador SHALL poder desativar e reativar colaboradores, com confirmação. Um colaborador desativado MUST NOT conseguir entrar, e sua sessão ativa SHALL deixar de valer. Técnicos inativos MUST NOT ser oferecidos para novas atribuições, mas SHALL continuar exibidos no histórico das ordens.

#### Scenario: Colaborador desativado
- **WHEN** o administrador desativa um atendente com sessão aberta
- **THEN** a próxima ação desse atendente o leva ao login, e o login com a senha dele é recusado

### Requirement: Proteção da administração

O administrador MUST NOT desativar a própria conta nem retirar o próprio cargo de Administrador, e o sistema MUST manter ao menos um administrador ativo.

#### Scenario: Autodesativação
- **WHEN** o administrador tenta desativar a própria conta
- **THEN** a operação é recusada com a mensagem de que não é possível desativar a própria conta

#### Scenario: Último administrador
- **WHEN** existe um único administrador ativo e há uma tentativa de mudar o cargo dele ou desativá-lo
- **THEN** a operação é recusada com a mensagem de que é necessário manter ao menos um administrador ativo

### Requirement: Redefinição de senha

O administrador SHALL poder definir uma nova senha provisória para um colaborador, respeitando a política de senha; a senha anterior SHALL deixar de valer.

#### Scenario: Nova senha provisória
- **WHEN** o administrador redefine a senha de um técnico
- **THEN** o técnico entra com a nova senha e a senha anterior é recusada
