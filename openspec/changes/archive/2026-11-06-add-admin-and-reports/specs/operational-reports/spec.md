# Spec Delta

## Purpose

Define os relatórios operacionais e financeiros do Assistência TECH por período e a exportação das ordens de serviço em formato de planilha, para apoiar a gestão da assistência.

## ADDED Requirements

### Requirement: Acesso aos relatórios

Os relatórios SHALL estar disponíveis para Administrador e Atendente; Técnico e Cliente SHALL ver a página de acesso negado.

#### Scenario: Técnico abre os relatórios
- **WHEN** um técnico abre `/admin/relatorios`
- **THEN** ele é levado à página de acesso negado

### Requirement: Período do relatório

Os relatórios SHALL considerar um período com data inicial e final, inclusivas, com padrão dos últimos 90 dias até a data atual. Uma data inicial posterior à final MUST ser recusada com mensagem.

#### Scenario: Período inválido
- **WHEN** o usuário informa data inicial posterior à data final
- **THEN** o relatório não é atualizado e a interface informa que o período é inválido

### Requirement: Volume de ordens

O relatório SHALL exibir a quantidade de ordens abertas no período e, entre elas, quantas estão entregues, canceladas e em andamento.

#### Scenario: Contagem no período
- **WHEN** o período contém 7 ordens abertas, 1 entregue e 1 cancelada
- **THEN** o relatório exibe 7 abertas, 1 entregue, 1 cancelada e 5 em andamento

### Requirement: Valores recebidos

O relatório SHALL exibir o total recebido no período, considerando a data de cada pagamento, e o total por forma de pagamento, além do ticket médio das ordens entregues no período.

#### Scenario: Recebimentos por forma
- **WHEN** o período contém pagamentos de R$ 225,00 e R$ 100,00 em PIX
- **THEN** o relatório exibe R$ 325,00 recebidos, todos em PIX

### Requirement: Produção por técnico

O relatório SHALL exibir, para cada técnico com ordens no período, a quantidade de ordens atribuídas, a quantidade concluídas ou entregues e o valor total orçado.

#### Scenario: Técnico com ordens concluídas
- **WHEN** um técnico tem no período uma ordem entregue e uma em reparo
- **THEN** a linha do técnico mostra 2 atribuídas e 1 concluída

### Requirement: Tempo médio de reparo

O relatório SHALL exibir o tempo médio, em dias, entre a abertura e a primeira mudança para Concluído das ordens que chegaram a esse status, e SHALL indicar quando não houver ordens suficientes para o cálculo.

#### Scenario: Sem ordens concluídas
- **WHEN** nenhuma ordem do período chegou a Concluído
- **THEN** o relatório exibe "—" no tempo médio de reparo

### Requirement: Exportação CSV

O sistema SHALL exportar as ordens abertas no período em CSV com cabeçalho, separador `;`, valores com vírgula decimal e codificação UTF-8 com BOM, com código, data de abertura, cliente, equipamento, problema relatado, técnico, status, total, valor pago e saldo. Campos com `;`, aspas ou quebras de linha MUST ser protegidos por aspas.

#### Scenario: Download
- **WHEN** o usuário aciona "Exportar CSV" com um período que contém ordens
- **THEN** é baixado o arquivo `ordens-AAAA-MM-DD-a-AAAA-MM-DD.csv` com uma linha por ordem do período

#### Scenario: Texto com separador
- **WHEN** o problema relatado ou o nome contém `;`
- **THEN** o campo é exportado entre aspas e a planilha mantém as colunas corretas
