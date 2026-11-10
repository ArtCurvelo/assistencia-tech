# Proposal: Quadro Kanban das ordens de serviço

## Why

A lista de ordens mostra uma ordem por linha; para ver o fluxo da oficina (quanto está em análise, quanto espera o cliente, quanto está pronto) é preciso filtrar status por status. Um quadro com uma coluna por status mostra a operação inteira de uma vez e deixa mover cada ordem para a próxima etapa sem abrir o detalhe.

## What Changes

- Página `/admin/ordens/quadro` com uma coluna por status (Recebido → Entregue e Cancelado), a quantidade de ordens em cada uma e um cartão por ordem: código, cliente, equipamento, técnico e selo de atraso.
- Cada cartão oferece botões "Mover para …" apenas para as transições que o usuário pode fazer naquela ordem (mesmas regras do detalhe). O cancelamento não aparece no quadro, porque exige motivo: o cartão leva ao detalhe.
- As colunas Entregue e Cancelado mostram as 8 ordens mais recentes, com link para a lista completa.
- Link "Quadro" na navegação e na página de ordens.

## Capabilities

### New Capabilities

- `orders-board`: quadro Kanban das ordens.

### Modified Capabilities

- Nenhuma.

## Impact

- **Código:** presenters (`board_columns`), estado e página do quadro, navegação, CSS.
- **Backend:** nenhuma mudança; usa as leituras e a alteração de status existentes.
- **Testes:** montagem das colunas, transições por perfil e limite das colunas finais.

## Out of Scope

- Arrastar e soltar (o botão "Mover para" funciona com mouse, teclado e leitor de tela).
