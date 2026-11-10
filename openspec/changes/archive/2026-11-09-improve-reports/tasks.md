# Tasks

## 1. Evolução mensal

- [x] 1.1 `monthly_series` em `domain/reports.py` e gráfico na página; testes.

## 2. PDF

- [x] 2.1 Botão "Imprimir / salvar PDF" e regras de impressão (navegação, formulário e botões ocultos, folha clara).

## 3. Verificação

- [x] 3.1 `pytest`, `openspec validate --strict` e conferência no navegador (gráfico e simulação das regras de impressão).

## Registro de verificação (2026-11-09)

- **pytest:** 4 testes novos em `tests/test_reports_monthly.py` (meses vazios, virada de ano, recebido por mês, entregues pela data da entrega, rótulos).
- **Navegador (demonstração):** gráfico de jun/26 a nov/26 com 7 abertas e 1 entregue em outubro; a animação das séries foi desligada porque, com a aba sem desenho, as barras não apareciam (também deixa a impressão estável).
- **Impressão simulada:** barra lateral, formulário e botões ocultos; "Período: 11/08/2026 a 09/11/2026" visível; painéis com fundo branco e texto escuro.
