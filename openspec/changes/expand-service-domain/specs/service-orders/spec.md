# Spec Delta

## Purpose

Define o ciclo de vida da ordem de serviço na assistência técnica: abertura, status e transições, técnico responsável, diagnóstico, orçamento de serviços e peças, pagamentos, histórico de alterações e consulta pública pelo cliente.

## ADDED Requirements

### Requirement: Abertura da ordem de serviço

A abertura de uma ordem SHALL exigir um cliente existente, um equipamento pertencente a esse cliente e o problema relatado. A ordem SHALL ser criada com o status Recebido, a data e hora de abertura e um código único no formato `OS-AAAA-NNNNN`.

#### Scenario: Abertura válida
- **WHEN** o usuário abre uma ordem para um cliente, escolhendo um equipamento desse cliente e descrevendo o problema
- **THEN** a ordem é criada com status Recebido, data de abertura e código único

#### Scenario: Equipamento de outro cliente
- **WHEN** a abertura referencia um equipamento que pertence a outro cliente
- **THEN** a ordem não é criada e a interface informa que o equipamento não pertence ao cliente selecionado

### Requirement: Conjunto de status da ordem

O status da ordem SHALL ser um dos valores Recebido, Em análise, Aguardando aprovação, Em reparo, Concluído, Entregue ou Cancelado.

#### Scenario: Status desconhecido
- **WHEN** uma alteração tenta atribuir um status fora do conjunto
- **THEN** a alteração é recusada e o status anterior é mantido

### Requirement: Transições de status permitidas

O sistema SHALL permitir somente as transições: Recebido → Em análise; Em análise → Aguardando aprovação; Aguardando aprovação → Em reparo; Em reparo → Concluído; Concluído → Entregue; Cancelado → Entregue; e de Recebido, Em análise, Aguardando aprovação ou Em reparo para Cancelado. Entregue é um status final.

#### Scenario: Transição válida
- **WHEN** o usuário altera para Em análise uma ordem em Recebido que possui técnico responsável
- **THEN** o status passa a ser Em análise

#### Scenario: Salto de etapa
- **WHEN** o usuário tenta alterar diretamente de Recebido para Concluído
- **THEN** a alteração é recusada com a mensagem de que a transição não é permitida, indicando os próximos status possíveis

#### Scenario: Ordem entregue
- **WHEN** o usuário tenta alterar o status de uma ordem Entregue
- **THEN** a alteração é recusada porque a ordem está finalizada

#### Scenario: Opções de status na interface
- **WHEN** o usuário abre o seletor de status de uma ordem
- **THEN** são oferecidos apenas os status permitidos a partir do status atual

### Requirement: Técnico responsável

O sistema SHALL permitir atribuir e trocar o técnico responsável por uma ordem que não esteja Entregue nem Cancelada. Uma ordem MUST ter técnico responsável para passar de Recebido a Em análise; o cancelamento de uma ordem recebida não exige técnico.

#### Scenario: Início da análise sem técnico
- **WHEN** o usuário tenta mover para Em análise uma ordem sem técnico responsável
- **THEN** a alteração é recusada com a mensagem de que é preciso atribuir um técnico

#### Scenario: Troca de técnico
- **WHEN** o usuário troca o técnico responsável de uma ordem Em reparo
- **THEN** o novo técnico passa a ser exibido na ordem e a troca é registrada no histórico

### Requirement: Diagnóstico técnico

O sistema SHALL permitir registrar e atualizar o diagnóstico técnico da ordem enquanto ela estiver Em análise, Aguardando aprovação ou Em reparo. A ordem MUST ter diagnóstico registrado para passar a Aguardando aprovação.

#### Scenario: Envio para aprovação sem diagnóstico
- **WHEN** o usuário tenta mover para Aguardando aprovação uma ordem sem diagnóstico
- **THEN** a alteração é recusada com a mensagem de que o diagnóstico é obrigatório

### Requirement: Orçamento com serviços e peças

O sistema SHALL permitir adicionar e remover itens de orçamento do tipo serviço (descrição e valor) e peça (descrição, quantidade inteira positiva e valor unitário) enquanto a ordem estiver Em análise, Aguardando aprovação ou Em reparo. Valores MUST ser positivos, em reais, com no máximo duas casas decimais.

#### Scenario: Inclusão de peça
- **WHEN** o usuário adiciona a peça "SSD 480 GB" com quantidade 1 e valor unitário R$ 250,00
- **THEN** a peça aparece no orçamento com subtotal de R$ 250,00

#### Scenario: Valor inválido
- **WHEN** o usuário adiciona um serviço com valor zero ou negativo
- **THEN** o item não é adicionado e a interface informa que o valor deve ser positivo

#### Scenario: Ordem concluída
- **WHEN** o usuário tenta adicionar um item a uma ordem Concluída
- **THEN** o item não é adicionado porque o orçamento não pode mais ser alterado

#### Scenario: Envio para aprovação sem itens
- **WHEN** o usuário tenta mover para Aguardando aprovação uma ordem com diagnóstico, mas sem itens de orçamento
- **THEN** a alteração é recusada com a mensagem de que o orçamento precisa ter ao menos um item

### Requirement: Valores da ordem

O sistema SHALL calcular o total dos serviços, o total das peças, o valor total, o valor pago e o saldo devedor da ordem, e SHALL exibi-los no formato monetário brasileiro (`R$ 1.234,56`).

#### Scenario: Cálculo do total
- **WHEN** a ordem possui um serviço de R$ 120,00 e duas unidades de uma peça de R$ 45,50
- **THEN** o total de serviços é R$ 120,00, o total de peças é R$ 91,00 e o valor total é R$ 211,00

### Requirement: Registro de pagamentos

O sistema SHALL permitir registrar pagamentos com valor e forma de pagamento (Dinheiro, PIX, Cartão de débito ou Cartão de crédito) em ordens não canceladas, e SHALL indicar a situação do pagamento como Pendente, Parcial ou Pago. Um pagamento MUST NOT exceder o saldo devedor.

#### Scenario: Pagamento parcial
- **WHEN** o usuário registra R$ 100,00 em PIX numa ordem de R$ 211,00 sem pagamentos
- **THEN** o valor pago passa a R$ 100,00, o saldo a R$ 111,00 e a situação a Parcial

#### Scenario: Pagamento acima do saldo
- **WHEN** o usuário tenta registrar um pagamento maior que o saldo devedor
- **THEN** o pagamento é recusado com a mensagem que informa o saldo atual

### Requirement: Entrega condicionada à quitação

Uma ordem Concluída MUST ter saldo devedor zero para passar a Entregue. Uma ordem Cancelada SHALL poder passar a Entregue sem exigência de pagamento, representando a devolução do equipamento.

#### Scenario: Entrega com saldo pendente
- **WHEN** o usuário tenta marcar como Entregue uma ordem Concluída com saldo devedor
- **THEN** a alteração é recusada com a mensagem que informa o saldo a receber

### Requirement: Cancelamento com motivo

O cancelamento de uma ordem SHALL exigir confirmação e o registro de um motivo.

#### Scenario: Cancelamento sem motivo
- **WHEN** o usuário tenta cancelar uma ordem sem informar o motivo
- **THEN** a ordem não é cancelada e a interface solicita o motivo

### Requirement: Histórico de alterações da ordem

O sistema SHALL registrar, em ordem cronológica e sem possibilidade de edição ou exclusão, cada evento da ordem: abertura, mudança de status (com status anterior, novo status e motivo, quando houver), atribuição ou troca de técnico, registro de diagnóstico, inclusão ou remoção de item e registro de pagamento, com data, hora e autor.

#### Scenario: Linha do tempo da ordem
- **WHEN** o usuário abre o detalhe de uma ordem que foi aberta, recebeu técnico e passou a Em análise
- **THEN** a linha do tempo exibe os três eventos em ordem cronológica, com data, hora e autor

### Requirement: Detalhe da ordem de serviço

O sistema SHALL oferecer uma página de detalhe de cada ordem, acessível pelo código, com cliente, equipamento, problema relatado, técnico, diagnóstico, orçamento, valores, pagamentos, status e histórico, e com as ações permitidas no status atual.

#### Scenario: Código inexistente
- **WHEN** o usuário acessa o detalhe de um código de ordem que não existe
- **THEN** a página informa que a ordem não foi encontrada e oferece retorno à lista

### Requirement: Pesquisa e filtro de ordens

A lista de ordens SHALL permitir pesquisa por código, cliente ou equipamento e filtro por status e por técnico responsável.

#### Scenario: Filtro por status
- **WHEN** o usuário filtra a lista pelo status Aguardando aprovação
- **THEN** somente as ordens nesse status são exibidas

### Requirement: Consulta pública da ordem

A consulta pública por código SHALL exibir apenas o código, o status, o tipo e modelo do equipamento e a data da última atualização, e MUST NOT exibir dados pessoais do cliente, valores ou diagnóstico.

#### Scenario: Consulta de ordem existente
- **WHEN** um visitante consulta um código de ordem existente na página inicial
- **THEN** são exibidos o status, o equipamento e a data da última atualização, sem nome, CPF, telefone ou e-mail do cliente
