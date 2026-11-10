# Proposal: Evolução mensal e relatório em PDF

## Why

Os relatórios mostram números de um período, mas não a tendência: não dá para ver se a assistência está abrindo mais ordens ou recebendo mais do que nos meses anteriores. E o único formato de saída é o CSV, bom para planilhas, mas não para entregar ou arquivar um relatório gerencial.

## What Changes

- **Evolução mensal:** gráfico dos últimos 6 meses com ordens abertas, ordens entregues e valor recebido em cada mês.
- **Imprimir / salvar PDF:** botão que imprime o relatório com folha clara, sem a navegação, o formulário de período e os botões, como no comprovante.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `operational-reports`: evolução mensal e impressão em PDF.

## Impact

- **Código:** `domain/reports.py` (`monthly_series`), presenters, estado e página de relatórios, CSS de impressão.
- **Backend:** nenhuma mudança.
- **Testes:** série mensal (meses sem movimento, virada de ano, pagamentos por mês).
