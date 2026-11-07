# access-control Specification

## Purpose
Define os perfis de acesso do Assistência TECH, as permissões de cada perfil e como elas são aplicadas às páginas e às operações, para que cada pessoa realize apenas o que o seu cargo permite.

## Requirements

### Requirement: Perfis de acesso

Todo usuário SHALL ter exatamente um perfil entre Administrador, Atendente, Técnico e Cliente. Um usuário com perfil Técnico MUST estar associado a um técnico cadastrado, e um usuário com perfil Cliente MUST estar associado a um cliente cadastrado.

#### Scenario: Perfil exibido
- **WHEN** um colaborador autenticado abre qualquer página administrativa
- **THEN** a interface exibe seu nome e seu perfil

### Requirement: Matriz de permissões

As permissões SHALL ser concedidas por perfil conforme a matriz: Administrador tem todas as permissões administrativas; Atendente vê painel, clientes, equipamentos e ordens, cadastra e edita clientes e equipamentos, abre ordens, atribui técnico, registra aprovação, pagamentos, entrega e cancelamento; Técnico vê painel, clientes, equipamentos e ordens, e registra diagnóstico, orçamento e status técnicos; Cliente acessa apenas o portal. Somente o Administrador exclui clientes e equipamentos.

#### Scenario: Atendente tenta excluir cliente
- **WHEN** um atendente tenta excluir um cliente
- **THEN** a operação é recusada com a mensagem de que o perfil não tem permissão para essa ação

#### Scenario: Técnico tenta registrar pagamento
- **WHEN** um técnico tenta registrar um pagamento
- **THEN** a operação é recusada por falta de permissão

### Requirement: Permissões por mudança de status

As mudanças de status SHALL exigir permissões específicas: iniciar análise, enviar para aprovação e concluir o reparo são ações técnicas (Administrador e Técnico); registrar a aprovação do orçamento (Aguardando aprovação → Em reparo), entregar e cancelar são ações de atendimento (Administrador e Atendente). O Cliente SHALL poder aprovar ou recusar, pelo portal, somente o orçamento das próprias ordens em "Aguardando aprovação"; nenhuma outra mudança de status é permitida ao Cliente.

#### Scenario: Atendente registra aprovação
- **WHEN** um atendente move uma ordem de Aguardando aprovação para Em reparo
- **THEN** o status é alterado e o histórico registra o atendente como autor

#### Scenario: Técnico tenta entregar
- **WHEN** um técnico tenta mover uma ordem Concluída para Entregue
- **THEN** a alteração é recusada por falta de permissão

#### Scenario: Cliente decide o próprio orçamento
- **WHEN** um cliente aprova pelo portal o orçamento de uma ordem própria em Aguardando aprovação
- **THEN** o status é alterado para Em reparo e o histórico registra o cliente como autor

#### Scenario: Colaborador tenta usar a decisão do cliente
- **WHEN** um colaborador tenta registrar uma decisão pelo recurso do portal
- **THEN** a operação é recusada por falta de permissão

### Requirement: Escopo do técnico

Um usuário Técnico SHALL alterar somente as ordens em que é o técnico responsável; as demais ordens SHALL ficar disponíveis apenas para consulta.

#### Scenario: Ordem de outro técnico
- **WHEN** um técnico tenta registrar diagnóstico em uma ordem atribuída a outro técnico
- **THEN** a operação é recusada com a mensagem de que a ordem pertence a outro técnico

#### Scenario: Ordem própria
- **WHEN** um técnico registra diagnóstico em uma ordem em que é o responsável
- **THEN** o diagnóstico é registrado

### Requirement: Verificação nas operações

As permissões MUST ser verificadas pelo sistema em cada operação de dados, independentemente do que a interface exibe; uma operação não permitida MUST ser recusada sem alterar dados.

#### Scenario: Operação enviada sem o botão correspondente
- **WHEN** uma operação de cadastro de cliente chega ao sistema em nome de um técnico
- **THEN** o cliente não é criado e a operação é recusada por falta de permissão

#### Scenario: Operação sem sessão
- **WHEN** uma operação administrativa é acionada sem sessão válida
- **THEN** a operação é recusada e o usuário é levado ao login

### Requirement: Proteção de rotas administrativas

As páginas em `/admin` SHALL exigir sessão válida de um colaborador. Sem sessão, o visitante SHALL ser levado ao login com indicação da página pretendida; com sessão de um perfil sem permissão, SHALL ver uma página de acesso negado com retorno à sua área.

#### Scenario: Visitante sem sessão
- **WHEN** um visitante sem sessão abre `/admin/clientes`
- **THEN** ele é levado ao login e nenhum dado de cliente é exibido

#### Scenario: Cliente tenta abrir o painel
- **WHEN** um usuário com perfil Cliente abre `/admin`
- **THEN** ele vê a página de acesso negado com um link para o portal

### Requirement: Interface conforme o perfil

Menus, botões e formulários de ações não permitidas ao perfil MUST NOT ser exibidos ou SHALL ser exibidos desabilitados, e o menu público SHALL mostrar "Entrar" para visitantes e o acesso à área do usuário para quem estiver autenticado.

#### Scenario: Técnico na página de clientes
- **WHEN** um técnico abre a página de clientes
- **THEN** a lista é exibida sem o formulário de cadastro e sem os botões de editar e excluir

#### Scenario: Visitante no menu público
- **WHEN** um visitante sem sessão abre a página inicial
- **THEN** o menu exibe "Entrar" e "Criar conta" e não exibe o link do painel administrativo
