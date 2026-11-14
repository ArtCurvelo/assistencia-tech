# Spec Delta

## ADDED Requirements

### Requirement: Navegação administrativa recolhível

Em telas com até 900 px de largura, a navegação administrativa SHALL ser exibida como uma barra superior compacta com um botão de menu que abre e fecha a lista de páginas e o bloco do usuário; em telas maiores, SHALL permanecer como barra lateral fixa.

#### Scenario: Abrir o menu no celular
- **WHEN** um colaborador abre uma página administrativa em um celular e aciona o botão de menu
- **THEN** a lista de páginas, seu nome, seu perfil e a opção "Sair" são exibidos

#### Scenario: Conteúdo visível sem rolar
- **WHEN** um colaborador abre o painel administrativo em um celular
- **THEN** o título da página aparece na primeira tela, sem que a navegação ocupe a tela inteira

#### Scenario: Escolha de uma página
- **WHEN** o colaborador escolhe uma página no menu aberto
- **THEN** a página é exibida e o menu é fechado

### Requirement: Tabelas contidas na largura da tela

Tabelas e painéis SHALL respeitar a largura disponível; quando uma tabela não couber, a rolagem horizontal SHALL ficar restrita à própria tabela, e a página MUST NOT ser mais larga que a tela.

#### Scenario: Lista de ordens no celular
- **WHEN** a lista de ordens de serviço é aberta em uma tela de 375 px
- **THEN** a largura da página é igual à da tela e a tabela pode ser rolada horizontalmente dentro do seu painel

### Requirement: Indicadores adaptáveis

Os indicadores do painel SHALL ser exibidos em 2 colunas em telas pequenas e em 4 colunas em telas grandes, sem quebrar valores numéricos ou monetários no meio.

#### Scenario: Valor a receber no celular
- **WHEN** o painel é aberto em uma tela de 375 px
- **THEN** o valor a receber é exibido em uma única linha
