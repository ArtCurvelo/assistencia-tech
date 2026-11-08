# service-orders Specification

## Purpose
Define o ciclo de vida da ordem de serviço na assistência técnica: abertura, status e transições, técnico responsável, diagnóstico, orçamento de serviços e peças, pagamentos, histórico de alterações e consulta pública pelo cliente.

## Requirements

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

O sistema SHALL permitir adicionar e remover itens de orçamento do tipo serviço (descrição e valor) e peça (descrição, quantidade inteira positiva e valor unitário) enquanto a ordem estiver Em análise, Aguardando aprovação ou Em reparo. A peça SHALL poder vir do catálogo de estoque, com nome e preço do catálogo, ou ser avulsa. Valores MUST ser positivos, em reais, com no máximo duas casas decimais.

#### Scenario: Inclusão de peça
- **WHEN** o usuário adiciona a peça "SSD 480 GB" com quantidade 1 e valor unitário R$ 250,00
- **THEN** a peça aparece no orçamento com subtotal de R$ 250,00

#### Scenario: Inclusão de peça do catálogo
- **WHEN** o usuário escolhe no catálogo a peça "Fonte 65 W" (R$ 180,00) com quantidade 1
- **THEN** o item aparece com o nome e o preço do catálogo e a peça tem uma unidade a menos em estoque

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

A consulta pública por código SHALL exibir apenas o código, o status, o tipo e modelo do equipamento, a previsão de entrega e a data da última atualização, e MUST NOT exibir dados pessoais do cliente, valores ou diagnóstico.

#### Scenario: Consulta de ordem existente
- **WHEN** um visitante consulta um código de ordem existente na página inicial
- **THEN** são exibidos o status, o equipamento, a previsão de entrega e a data da última atualização, sem nome, CPF, telefone ou e-mail do cliente

### Requirement: Previsão de entrega

Toda ordem SHALL ter uma previsão de entrega, informada na abertura ou, sem informação, igual à data de abertura mais 7 dias. A previsão MUST NOT ser anterior à data de abertura. Administrador e Atendente SHALL poder alterá-la enquanto a ordem não estiver Entregue ou Cancelada, e cada alteração SHALL ser registrada no histórico.

#### Scenario: Previsão padrão
- **WHEN** o atendente abre uma ordem em 10/11/2026 sem informar a previsão
- **THEN** a previsão de entrega é 17/11/2026

#### Scenario: Alteração da previsão
- **WHEN** o atendente altera a previsão de uma ordem Em reparo para 20/11/2026
- **THEN** a nova previsão é exibida e o histórico registra a alteração com autor e data

#### Scenario: Previsão anterior à abertura
- **WHEN** alguém informa uma previsão anterior à data de abertura
- **THEN** a previsão é recusada com a mensagem correspondente

### Requirement: Ordens atrasadas

Uma ordem antes de Concluído com previsão de entrega anterior a hoje SHALL ser identificada como "Atrasada", com os dias de atraso, na lista de ordens e no detalhe. O painel SHALL exibir quantas ordens estão atrasadas.

#### Scenario: Ordem atrasada
- **WHEN** uma ordem Em reparo tem previsão de entrega de três dias atrás
- **THEN** ela aparece como "Atrasada há 3 dias" na lista e no detalhe e é contada no alerta do painel

#### Scenario: Ordem concluída não fica atrasada
- **WHEN** uma ordem Concluída tem previsão vencida
- **THEN** ela não é marcada como atrasada

### Requirement: Garantia do serviço

Uma ordem entregue depois de Concluída SHALL ter garantia de 90 dias a partir da data da entrega, exibida como "Garantia até" no detalhe. A entrega de uma ordem cancelada MUST NOT gerar garantia.

#### Scenario: Garantia após a entrega
- **WHEN** uma ordem concluída é entregue em 07/11/2026
- **THEN** o detalhe exibe "Garantia até 05/02/2027"

#### Scenario: Ordem cancelada
- **WHEN** uma ordem cancelada é marcada como entregue
- **THEN** nenhuma garantia é exibida

### Requirement: Ordem em garantia

Dentro do prazo de garantia, Administrador e Atendente SHALL poder abrir, a partir da ordem original, uma nova ordem ligada a ela, para o mesmo cliente e equipamento. A ordem em garantia SHALL registrar serviços e peças no orçamento sem gerar valor a pagar, e a abertura SHALL citar a ordem original no histórico. Fora do prazo, a abertura em garantia MUST ser recusada.

#### Scenario: Abertura em garantia
- **WHEN** o atendente abre uma ordem em garantia da OS-2026-00001, entregue há 10 dias
- **THEN** a nova ordem fica ligada à OS-2026-00001, com o mesmo cliente e equipamento, e o detalhe mostra "Ordem em garantia da OS-2026-00001"

#### Scenario: Orçamento sem cobrança
- **WHEN** uma peça de R$ 180,00 é incluída numa ordem em garantia
- **THEN** a peça aparece no orçamento, o total a pagar é R$ 0,00 e a situação do pagamento é "Garantia"

#### Scenario: Garantia vencida
- **WHEN** alguém tenta abrir uma ordem em garantia de uma ordem entregue há 91 dias
- **THEN** a abertura é recusada com a mensagem de que a garantia terminou

### Requirement: Consulta pública por link

O sistema SHALL oferecer a página pública `/consulta/<código>`, que abre a consulta da ordem já preenchida e exibe os mesmos dados limitados da consulta pública. Códigos fora do formato `OS-AAAA-NNNNN` MUST receber a mensagem de código não encontrado sem consulta ao backend.

#### Scenario: QR code lido pelo celular
- **WHEN** o cliente abre `/consulta/OS-2026-00125`
- **THEN** a página mostra o status, o equipamento, a previsão de entrega e a última atualização da ordem, sem dados pessoais nem valores

#### Scenario: Código inválido no link
- **WHEN** alguém abre `/consulta/qualquer-coisa`
- **THEN** a página informa que o código não foi encontrado
