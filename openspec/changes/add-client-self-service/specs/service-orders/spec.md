# Spec Delta

## MODIFIED Requirements

### Requirement: Conjunto de status da ordem

O status da ordem SHALL ser um dos valores Solicitado, Recebido, Em análise, Aguardando aprovação, Em reparo, Concluído, Entregue ou Cancelado.

#### Scenario: Status desconhecido
- **WHEN** uma alteração tenta atribuir um status fora do conjunto
- **THEN** a alteração é recusada e o status anterior é mantido

## ADDED Requirements

### Requirement: Recebimento de ordens solicitadas

Uma ordem em Solicitado SHALL poder ir apenas para Recebido, por Administrador ou Atendente, ou para Cancelado, com motivo. Ao confirmar o recebimento, a previsão de entrega SHALL ser definida como a data do recebimento mais 7 dias. Ordens em Solicitado MUST NOT contar como atrasadas. O detalhe da ordem SHALL exibir a forma de entrega e, na coleta por motoboy, o endereço e o período.

#### Scenario: Confirmação do recebimento
- **WHEN** a atendente confirma o recebimento de uma ordem solicitada em 16/11/2026
- **THEN** a ordem passa a Recebido com previsão de entrega em 23/11/2026

#### Scenario: Técnico tenta receber
- **WHEN** um técnico tenta mover uma ordem de Solicitado para Recebido
- **THEN** a mudança é recusada por falta de permissão
