# Tasks

## 1. Domínio e configuração

- [x] 1.1 Criar `domain/receipt.py` (tipo do comprovante, endereço da consulta, validação do código e QR code em SVG com `segno`) e `ASSISTENCIA_PUBLIC_URL` em `config.py`; verificar com testes.

## 2. Interface

- [x] 2.1 Montar a visão do comprovante nos presenters e as páginas `/admin/ordens/<código>/comprovante` e `/minha-conta/ordens/<código>/comprovante`, com botão "Imprimir / salvar PDF", estilos de impressão e links no detalhe da ordem e no portal.
- [x] 2.2 Criar a consulta pública por link `/consulta/<código>`.

## 3. Verificação

- [x] 3.1 Executar `pytest` e `openspec validate add-order-receipt --strict`; conferir no navegador o comprovante de entrada, o de entrega, a impressão e o endereço do QR code, e montar os comprovantes com dados reais do Xano; registrar os resultados.

## Registro de verificação (2026-11-08)

- **pytest (.venv):** 417 passed (11 testes novos em `tests/test_order_receipt.py`).
- **OpenSpec:** `openspec validate add-order-receipt --strict` válido.
- **Navegador (modo demonstração):**
  - OS-2026-00120 (entregue) → "Comprovante de entrega" com itens, pagamento PIX, entrega em 04/10/2026 e "Garantia até 02/01/2027"; CPF `***.***.***-98`;
  - OS-2026-00121 (cancelada) → "Comprovante de entrada" com status Cancelado e o motivo;
  - a imagem do QR code na página é idêntica à gerada pelo `segno` para `http://localhost:3000/consulta/OS-2026-00120`;
  - regras de impressão aplicadas → fundo branco, só o comprovante, sem barra de ações;
  - `/consulta/OS-2026-00125` → consulta preenchida (status, equipamento, previsão, atualização); `/consulta/qualquer-coisa` → "Código não encontrado", sem consulta ao backend;
  - cliente Marina → comprovante da própria OS-2026-00125; OS-2026-00120 (de outra cliente) → "Ordem não encontrada";
  - sem sessão, `/admin/ordens/OS-2026-00125/comprovante` → login com retorno ao comprovante.
- **Xano real** (código da aplicação, conta de teste da atendente):
  - OS-2026-00001 → comprovante de entrega, garantia até 05/02/2027;
  - OS-2026-00002 → comprovante de entrada; OS-2026-00003 → entrada com o motivo da recusa do cliente;
  - CPF completo ausente nos três; ordem inexistente → "Ordem de serviço não encontrada.".
- **Backend:** sem mudanças; nenhum envio ao Xano.
