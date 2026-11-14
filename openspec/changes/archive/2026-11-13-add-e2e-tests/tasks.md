# Tasks

## 1. Testes

- [x] 1.1 Escrever `e2e/` com Playwright e rodar contra o site de produção local em modo demonstração.
- [x] 1.2 Job "Ponta a ponta (navegador)" no CI.

## 2. Site acordado

- [x] 2.1 Workflow `keep-awake.yml` agendado, sem segredos.

## Registro de verificação (2026-11-13)

- **Local (Windows, Chromium do Playwright 1.65):** `reflex export --frontend-only --no-zip --env prod`, Granian em modo demonstração na porta 8000 e `pytest e2e` → 11 passed em 39 s.
- Na primeira rodada, 3 falhas eram dos testes: mensagem exibida em dois lugares (aviso e alerta) e navegação antes de a área do usuário carregar após o login; corrigidas nos testes.
- **Pendente:** primeira execução do job e do agendamento no GitHub, após o envio.
