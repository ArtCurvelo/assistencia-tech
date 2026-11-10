# Spec Delta

## ADDED Requirements

### Requirement: Evolução mensal

Os relatórios SHALL exibir um gráfico dos últimos 6 meses, incluindo o mês atual, com a quantidade de ordens abertas (pela data de abertura), de ordens entregues (pela data da entrega) e o valor recebido (pela data do pagamento) em cada mês. Meses sem movimento SHALL aparecer com zero.

#### Scenario: Mês sem movimento
- **WHEN** não houve ordens nem pagamentos em agosto
- **THEN** agosto aparece no gráfico com zero ordens e R$ 0,00 recebido

#### Scenario: Virada de ano
- **WHEN** o mês atual é fevereiro de 2027
- **THEN** o gráfico mostra de setembro de 2026 a fevereiro de 2027

### Requirement: Relatório em PDF

A página de relatórios SHALL ter o botão "Imprimir / salvar PDF", que imprime o relatório do período com folha clara e sem a navegação, o formulário de período e os botões.

#### Scenario: Impressão do relatório
- **WHEN** o usuário aciona "Imprimir / salvar PDF"
- **THEN** a impressão mostra apenas o título, o período e os indicadores, tabelas e gráficos do relatório
