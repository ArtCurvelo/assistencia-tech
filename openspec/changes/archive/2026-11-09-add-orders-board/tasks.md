# Tasks

## 1. Quadro

- [x] 1.1 `board_columns` nos presenters (colunas, contagens, limite das colunas finais, transições por usuário sem cancelamento); testes.
- [x] 1.2 Estado, página `/admin/ordens/quadro`, link na navegação e na página de ordens, CSS.

## 2. Verificação

- [x] 2.1 `pytest`, `openspec validate --strict` e conferência no navegador com Atendente e Técnico.

## Registro de verificação (2026-11-09)

- **pytest:** 4 testes novos em `tests/test_orders_board.py` (colunas e contagens, transições por perfil sem cancelamento, limite das colunas finais, entrega sem quitação recusada).
- **Navegador (demonstração, Atendente):** 7 colunas com contagens; "→ Em reparo" só na ordem aguardando aprovação e "→ Entregue" na concluída e na cancelada (devolução do equipamento, regra existente); entrega da OS-2026-00122 recusada com "Há saldo a receber de R$ 111,00. Registre o pagamento antes da entrega."; OS-2026-00123 movida para Em reparo, com as contagens atualizadas.
