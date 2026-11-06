# Spec Delta

## ADDED Requirements

### Requirement: Preservação dos dados em formulários

Quando uma operação enviada por formulário for recusada, a interface SHALL manter os valores digitados para correção; os campos SHALL ser limpos somente após uma operação concluída com sucesso.

#### Scenario: Cadastro recusado
- **WHEN** o usuário envia o cadastro de cliente com um CPF já cadastrado
- **THEN** a mensagem de erro é exibida e os demais campos continuam preenchidos

#### Scenario: Cadastro concluído
- **WHEN** o cadastro é concluído com sucesso
- **THEN** o formulário volta ao estado vazio

### Requirement: Gráficos do painel

O painel administrativo SHALL apresentar graficamente a distribuição das ordens por status e a situação dos pagamentos, com cores sólidas diferenciadas, rótulos e quantidades legíveis.

#### Scenario: Distribuição por status
- **WHEN** um colaborador abre o painel com ordens em vários status
- **THEN** o gráfico exibe cada status com sua quantidade

### Requirement: Indicadores indisponíveis

Quando os dados do painel não puderem ser carregados, os indicadores SHALL exibir "—" em vez de ficarem vazios, junto com a mensagem de falha.

#### Scenario: Backend sem contrato
- **WHEN** o painel é aberto com a fonte Xano sem contratos registrados
- **THEN** cada indicador exibe "—" e o alerta informa que a integração está pendente

### Requirement: Navegação por teclado

A interface SHALL oferecer um link "Pular para o conteúdo" como primeiro elemento focável das páginas administrativas e SHALL exibir indicação de foco visível em links, botões e campos.

#### Scenario: Primeiro Tab
- **WHEN** o usuário pressiona Tab ao abrir uma página administrativa
- **THEN** o link "Pular para o conteúdo" recebe o foco e, ao ser acionado, leva ao conteúdo principal

### Requirement: Página não encontrada

O acesso a uma rota inexistente SHALL exibir uma página "Página não encontrada" com link para a área do usuário ou para a página inicial.

#### Scenario: Endereço digitado errado
- **WHEN** o usuário acessa `/admin/relatorio-inexistente`
- **THEN** é exibida a página "Página não encontrada" com um link de retorno

### Requirement: Acesso ao login no celular

O cabeçalho público SHALL manter visíveis, em qualquer largura de tela, a ação "Entrar" para visitantes e a ação "Sair" para usuários autenticados.

#### Scenario: Visitante no celular
- **WHEN** um visitante abre a página inicial em um celular
- **THEN** o botão "Entrar" é exibido no cabeçalho
