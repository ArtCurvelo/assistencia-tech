# orders-board Specification

## Purpose
Define o quadro Kanban das ordens de serviço do Assistência TECH: uma coluna por status e a mudança de etapa pelos cartões, com as regras de transição de cada perfil.

## Requirements

### Requirement: Quadro por status

O sistema SHALL oferecer aos colaboradores um quadro com uma coluna por status da ordem, na ordem do fluxo, com a quantidade de ordens de cada coluna e um cartão por ordem com código, cliente, equipamento, técnico e o selo de atraso quando houver. As colunas Entregue e Cancelado SHALL mostrar até 8 ordens, as mais recentes, com link para a lista completa.

#### Scenario: Visão do fluxo
- **WHEN** a atendente abre o quadro
- **THEN** vê sete colunas, de Recebido a Cancelado, cada uma com a quantidade de ordens

#### Scenario: Muitas ordens entregues
- **WHEN** existem 20 ordens entregues
- **THEN** a coluna Entregue mostra as 8 mais recentes e o total 20

### Requirement: Mover ordens pelo quadro

Cada cartão SHALL oferecer "Mover para" somente as transições permitidas ao usuário naquela ordem, com as mesmas regras do detalhe da ordem. O cancelamento MUST NOT ser oferecido no quadro, porque exige motivo. Uma mudança recusada pelas regras (por exemplo, entrega sem quitação) SHALL exibir a mensagem do sistema sem alterar a ordem.

#### Scenario: Técnico em ordem de outro técnico
- **WHEN** um técnico vê o cartão de uma ordem atribuída a outro técnico
- **THEN** o cartão não oferece nenhum botão "Mover para"

#### Scenario: Entrega sem quitação
- **WHEN** a atendente tenta mover para Entregue uma ordem concluída com saldo devedor
- **THEN** o quadro exibe a mensagem de que a ordem precisa estar quitada e a ordem continua Concluída
