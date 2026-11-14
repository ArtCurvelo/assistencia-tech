# Proposal: Testes de ponta a ponta e site acordado

## Why

Os testes automáticos conferem regras e adaptadores, mas nenhum abre o site num navegador: um erro de tela (botão que some, login que não redireciona, foco invisível) passaria pelo CI. Duas tarefas de acessibilidade da mudança `refine-frontend-experience` estavam abertas por falta dessa conferência. Além disso, o site publicado no plano gratuito dorme após 15 minutos, o que atrapalha uma apresentação.

## What Changes

- **Testes de ponta a ponta** (`e2e/`, Playwright com Chromium) contra o site compilado em modo produção e servido em modo demonstração: página inicial, teclado (link "Pular para o conteúdo" e foco visível), serviços, consulta pública, proteção das páginas, painel e quadro da equipe, comprovante com QR code, portal do cliente e download dos dados.
- **CI:** novo job "Ponta a ponta (navegador)".
- **Site acordado:** workflow agendado que acessa `/ping` do site publicado a cada 10 minutos em horário comercial, sem segredos.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `continuous-integration`: testes de ponta a ponta no navegador.
- `public-deployment`: site mantido acordado.

## Impact

- **Arquivos:** `e2e/`, `requirements-e2e.txt`, `.github/workflows/ci.yml`, `.github/workflows/keep-awake.yml`, README.
- **Backend:** nenhuma mudança.
