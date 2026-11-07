# Spec Delta

## ADDED Requirements

### Requirement: Sessão com o token do backend

Com a fonte Xano, o login SHALL obter o token do backend e guardá-lo somente na sessão do servidor, associado ao token opaco do cookie. O token do backend MUST NOT ser enviado ao navegador. Cada requisição autenticada ao Xano SHALL usar o token da sessão do usuário que a originou, e uma requisição que exige login MUST NOT ser enviada sem esse token.

#### Scenario: Login guarda o token no servidor
- **WHEN** o usuário entra com credenciais válidas
- **THEN** o navegador recebe apenas o token opaco da sessão, e as chamadas seguintes ao Xano levam o token do backend daquela sessão

#### Scenario: Sem token na sessão
- **WHEN** uma operação que exige login é acionada sem token do backend na sessão
- **THEN** nenhuma requisição é enviada e o usuário é tratado como não autenticado

#### Scenario: Token recusado pelo backend
- **WHEN** o Xano responde que o token não é mais válido
- **THEN** a sessão é encerrada e o usuário é levado ao login com o aviso de sessão expirada

### Requirement: Projeções públicas e do portal no servidor

A consulta pública e o portal do cliente SHALL usar endpoints do backend que já devolvem somente os dados permitidos. A consulta pública MUST NOT exigir login e MUST NOT devolver dados pessoais, valores nem diagnóstico. O portal SHALL obter as ordens e o cadastro do cliente pelo token, nunca por um identificador enviado pelo navegador.

#### Scenario: Consulta pública sem dados pessoais
- **WHEN** um visitante consulta o código de uma ordem existente
- **THEN** recebe somente o código, o status, o equipamento e a data da última atualização

#### Scenario: Código com ano errado
- **WHEN** um visitante informa o número de uma ordem existente com um ano diferente do ano de abertura
- **THEN** a ordem é tratada como não encontrada

#### Scenario: Portal filtrado pelo token
- **WHEN** um cliente autenticado abre o portal
- **THEN** vê somente as próprias ordens, com equipamento, orçamento, pagamentos e andamento

#### Scenario: Token de cliente em endpoint de colaborador
- **WHEN** o token de um cliente é usado para listar clientes, ordens ou contas
- **THEN** o backend recusa a operação por falta de permissão

### Requirement: Mensagens das regras do backend

O sistema SHALL exibir ao usuário as mensagens das pré-condições do backend em XanoScript, escritas em português para o usuário final. Mensagens técnicas nativas do Xano MUST NOT ser exibidas: o usuário recebe a mensagem padrão da categoria do erro e o detalhe técnico fica somente no registro do servidor.

#### Scenario: Regra de negócio recusada pelo backend
- **WHEN** o backend recusa uma operação por uma pré-condição, por exemplo um CPF já cadastrado
- **THEN** o usuário vê a mensagem dessa pré-condição

#### Scenario: Erro técnico do Xano
- **WHEN** o Xano responde com uma mensagem técnica própria, por exemplo um parâmetro ausente
- **THEN** o usuário vê a mensagem padrão em português e o texto técnico não aparece na interface

### Requirement: Contas e técnicos no backend

Com a fonte Xano, o técnico SHALL ser a própria conta com perfil técnico, e o cadastro público de cliente SHALL criar o cliente e a conta de acesso numa única operação do backend, com a unicidade de CPF e e-mail verificada no servidor.

#### Scenario: Cadastro de técnico
- **WHEN** o administrador cadastra um colaborador com perfil técnico e especialidade
- **THEN** uma única conta é criada no backend e passa a aparecer na lista de técnicos para atribuição

#### Scenario: Autocadastro de cliente
- **WHEN** um visitante cria a conta pelo cadastro público
- **THEN** o cliente e a conta são criados juntos e o visitante entra no portal já autenticado

### Requirement: Limite de requisições do plano

O sistema SHALL respeitar o limite de requisições do plano do Xano, espaçando as chamadas e reaproveitando por poucos segundos leituras idênticas do mesmo usuário. Qualquer escrita SHALL descartar as leituras reaproveitadas. Ao receber a resposta de limite excedido, o sistema SHALL aguardar a janela do limite e tentar uma única vez de novo. Indisponibilidade do backend MUST NOT encerrar a sessão do usuário.

#### Scenario: Muitas leituras seguidas
- **WHEN** uma tela precisa de mais leituras do que o limite permite na janela
- **THEN** as chamadas são espaçadas e a tela carrega sem erro de limite

#### Scenario: Leitura após uma alteração
- **WHEN** o usuário grava uma alteração e a tela é recarregada
- **THEN** os dados exibidos vêm do backend, sem reaproveitar leituras anteriores à alteração

#### Scenario: Backend indisponível
- **WHEN** o backend fica indisponível durante a navegação de um usuário autenticado
- **THEN** a interface informa a indisponibilidade e o usuário continua com a sessão ativa

### Requirement: Contrato publicado conferido

Cada contrato registrado na aplicação SHALL corresponder a um endpoint do contrato-alvo, e o projeto SHALL oferecer um verificador que compara o contrato-alvo com a documentação publicada pelo Xano. O backend em XanoScript versionado SHALL atender a todo o contrato-alvo.

#### Scenario: Verificação do contrato
- **WHEN** o verificador é executado contra o workspace ou contra as cópias versionadas da documentação
- **THEN** todos os endpoints do contrato-alvo são relatados como atendidos

#### Scenario: Contrato fora do alvo
- **WHEN** alguém registra na aplicação um contrato que não existe no contrato-alvo
- **THEN** os testes automatizados falham

## MODIFIED Requirements

### Requirement: Tradução das respostas de erro

O sistema SHALL classificar as falhas de comunicação com o Xano em categorias compreensíveis — dados inválidos, sessão inválida, sem permissão, não encontrado, serviço indisponível e erro inesperado — com base no código de status HTTP da resposta. Sessão inválida SHALL encerrar a sessão; serviço indisponível MUST NOT encerrá-la.

#### Scenario: Recurso inexistente
- **WHEN** o backend responde que o registro solicitado não existe
- **THEN** a operação é classificada como não encontrada e o usuário recebe uma mensagem correspondente

#### Scenario: Erro interno do backend
- **WHEN** o backend responde com um erro de servidor
- **THEN** a operação é classificada como serviço indisponível, sem exibir o conteúdo técnico da resposta ao usuário

#### Scenario: Sessão inválida
- **WHEN** o backend responde que a requisição não está autenticada
- **THEN** a operação é classificada como sessão inválida, a sessão é encerrada e o usuário é levado ao login

#### Scenario: Acesso negado
- **WHEN** o backend responde que o usuário autenticado não tem permissão
- **THEN** a operação é classificada como sem permissão e o usuário recebe uma mensagem correspondente, mantendo a sessão
