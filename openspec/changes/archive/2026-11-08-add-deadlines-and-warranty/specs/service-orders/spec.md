# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Consulta pública da ordem

A consulta pública por código SHALL exibir apenas o código, o status, o tipo e modelo do equipamento, a previsão de entrega e a data da última atualização, e MUST NOT exibir dados pessoais do cliente, valores ou diagnóstico.

#### Scenario: Consulta de ordem existente
- **WHEN** um visitante consulta um código de ordem existente na página inicial
- **THEN** são exibidos o status, o equipamento, a previsão de entrega e a data da última atualização, sem nome, CPF, telefone ou e-mail do cliente
