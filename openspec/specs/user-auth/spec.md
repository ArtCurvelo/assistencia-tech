# user-auth Specification

## Purpose
Define como colaboradores e clientes se identificam no Assistência TECH: login, logout, sessão, cadastro de cliente, armazenamento seguro de senhas e proteção contra tentativas repetidas de acesso.

## Requirements

### Requirement: Login com e-mail e senha

O sistema SHALL autenticar usuários por e-mail e senha. Após o login, o usuário SHALL ser levado à página que tentava acessar ou, na ausência dela, à área inicial do seu perfil: painel administrativo para colaboradores e portal para clientes.

#### Scenario: Login de colaborador
- **WHEN** um atendente informa e-mail e senha corretos
- **THEN** a sessão é iniciada e ele é levado ao painel administrativo, com seu nome e perfil exibidos

#### Scenario: Retorno à página pretendida
- **WHEN** um visitante tenta abrir `/admin/ordens`, é levado ao login e entra com uma conta autorizada
- **THEN** ele é levado de volta a `/admin/ordens`

#### Scenario: Login de cliente
- **WHEN** um cliente informa e-mail e senha corretos
- **THEN** ele é levado ao portal do cliente

### Requirement: Mensagem genérica para credenciais inválidas

Quando o e-mail não existir ou a senha estiver incorreta, o sistema SHALL exibir a mesma mensagem, sem revelar qual dos dois está errado.

#### Scenario: Senha incorreta
- **WHEN** o usuário informa um e-mail cadastrado com a senha errada
- **THEN** a interface exibe "E-mail ou senha inválidos." e nenhuma sessão é iniciada

#### Scenario: E-mail inexistente
- **WHEN** o usuário informa um e-mail não cadastrado
- **THEN** a interface exibe a mesma mensagem "E-mail ou senha inválidos."

### Requirement: Bloqueio após tentativas malsucedidas

Após 5 tentativas de login malsucedidas para o mesmo e-mail em 15 minutos, o sistema SHALL recusar novas tentativas para esse e-mail por 5 minutos, mesmo com a senha correta, informando o tempo de espera.

#### Scenario: Sexta tentativa
- **WHEN** o usuário erra a senha 5 vezes seguidas e tenta novamente com a senha correta
- **THEN** o login é recusado com a mensagem de que o acesso está temporariamente bloqueado

#### Scenario: Fim do bloqueio
- **WHEN** os 5 minutos de bloqueio terminam
- **THEN** o usuário consegue entrar com a senha correta

### Requirement: Armazenamento seguro de senhas

O sistema MUST armazenar somente o hash da senha, gerado com sal aleatório por usuário e PBKDF2-SHA256, e MUST NOT registrar senhas em logs, mensagens ou histórico.

#### Scenario: Mesma senha para dois usuários
- **WHEN** dois usuários escolhem a mesma senha
- **THEN** os valores armazenados são diferentes e nenhum deles contém a senha em texto puro

### Requirement: Sessão com expiração por inatividade

A sessão SHALL ser identificada por um token aleatório guardado em cookie com `SameSite=Strict` e validado no servidor, e SHALL expirar após 2 horas sem atividade.

#### Scenario: Sessão expirada
- **WHEN** um usuário autenticado fica mais de 2 horas sem atividade e abre uma página administrativa
- **THEN** ele é levado ao login com a mensagem de que a sessão expirou

#### Scenario: Token desconhecido
- **WHEN** o navegador apresenta um token de sessão que o servidor não reconhece
- **THEN** o usuário é tratado como não autenticado

### Requirement: Logout

O sistema SHALL permitir encerrar a sessão a qualquer momento, invalidando o token no servidor e no navegador.

#### Scenario: Encerrar sessão
- **WHEN** o usuário aciona "Sair" e depois tenta abrir uma página administrativa
- **THEN** ele é levado ao login

### Requirement: Cadastro de cliente com conta de acesso

O cadastro público SHALL criar um cliente e uma conta com perfil Cliente, exigindo nome, CPF, e-mail, telefone, senha e confirmação da senha, com as mesmas validações e regras de unicidade do cadastro administrativo de clientes. Após o cadastro, o cliente SHALL entrar automaticamente no portal.

#### Scenario: Cadastro válido
- **WHEN** um visitante preenche o cadastro com dados válidos e senhas iguais
- **THEN** o cliente passa a existir na lista de clientes, a conta é criada e ele é levado ao portal

#### Scenario: Confirmação diferente
- **WHEN** a confirmação da senha difere da senha
- **THEN** nenhum cliente ou conta é criado e a interface informa que as senhas não conferem

#### Scenario: E-mail já usado por uma conta
- **WHEN** o visitante usa um e-mail que já pertence a uma conta
- **THEN** o cadastro é recusado com a mensagem de que o e-mail já está cadastrado

### Requirement: Política de senha

Senhas novas SHALL ter no mínimo 8 caracteres, com ao menos uma letra e um número.

#### Scenario: Senha fraca
- **WHEN** o visitante escolhe a senha `12345678`
- **THEN** o cadastro é recusado com a mensagem que descreve a política de senha

### Requirement: Usuários de demonstração

No modo demonstração, o sistema SHALL oferecer contas de teste para cada perfil e SHALL exibir na tela de login um acesso rápido a elas, identificado como demonstrativo. Fora do modo demonstração, esse acesso MUST NOT ser exibido.

#### Scenario: Acesso rápido no modo demonstração
- **WHEN** a tela de login é aberta no modo demonstração
- **THEN** são exibidos botões de acesso para Administrador, Atendente, Técnico e Cliente, identificados como contas de demonstração

#### Scenario: Fonte Xano
- **WHEN** a tela de login é aberta com a fonte Xano
- **THEN** o acesso rápido não é exibido
