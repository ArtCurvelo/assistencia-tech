# design-system Specification

## Purpose

Define uma identidade visual consistente para o Assistência TECH, garantindo que as páginas e os componentes da interface apresentem uma experiência moderna, legível e coerente.

## Requirements

### Requirement: Consistência visual

A interface SHALL utilizar padrões visuais consistentes para cores, tipografia, espaçamento, bordas e elementos interativos em todas as páginas contempladas pelo redesign.

#### Scenario: Padrões compartilhados entre páginas
- **WHEN** o usuário navega entre as páginas públicas, de autenticação e administrativas
- **THEN** os elementos visuais compartilhados mantêm a mesma identidade e os mesmos padrões de apresentação

### Requirement: Clareza dos elementos interativos

A interface SHALL apresentar os elementos interativos de forma reconhecível e fornecer feedback visual apropriado durante a interação.

#### Scenario: Interação com um botão
- **WHEN** o usuário posiciona o cursor ou aciona um botão
- **THEN** o botão apresenta um estado visual coerente com a interação e preserva sua função

### Requirement: Feedback de estado

A interface SHALL apresentar feedback visual compreensível para estados de carregamento, sucesso, erro e ausência de dados quando esses estados forem aplicáveis à funcionalidade exibida.

#### Scenario: Lista sem registros
- **WHEN** uma página administrativa apresenta uma lista sem registros
- **THEN** a interface informa que não há dados disponíveis, sem apresentar uma lista aparentemente quebrada

#### Scenario: Operação com erro
- **WHEN** uma operação retorna um erro que precisa ser comunicado ao usuário
- **THEN** a interface apresenta uma mensagem compreensível sem expor detalhes técnicos sensíveis

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

#### Scenario: Falha no carregamento
- **WHEN** um colaborador autenticado abre o painel e o carregamento dos dados falha
- **THEN** cada indicador exibe "—" e o alerta informa o motivo da falha

#### Scenario: Antes do primeiro carregamento
- **WHEN** o painel é exibido antes de os dados terem sido carregados
- **THEN** os indicadores exibem "—" em vez de ficarem vazios

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
