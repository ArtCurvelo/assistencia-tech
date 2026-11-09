# Proposal: Números reais na página inicial

## Why

A página inicial mostra "+500 Equipamentos reparados", "98% Clientes satisfeitos", "24h Meta de diagnóstico inicial" e "100% Transparência". Esses números vieram do protótipo e não saem do sistema: são dados fictícios apresentados como reais num site público, o que contradiz a regra do projeto de não substituir dados reais por fictícios. O sistema já registra o que esses cartões querem mostrar — ordens entregues, ordens em atendimento e avaliações dos clientes.

## What Changes

- Os quatro cartões passam a mostrar:
  - **Equipamentos entregues:** quantidade de ordens com status Entregue;
  - **Em atendimento agora:** ordens que não estão Entregues nem Canceladas;
  - **Satisfação (NPS):** o NPS de todas as avaliações, com a quantidade de respostas, ou "—" sem avaliações;
  - **Garantia:** "90 dias", regra fixa do sistema.
- **Xano:** endpoint público `GET /estatisticas_publicas` que devolve só contagens agregadas (entregues, em atendimento, avaliações, promotores, detratores), sem dados pessoais, valores ou identificadores.
- **Aplicação:** os números são guardados por 5 minutos no servidor, para que cada visita à página inicial não consuma o limite de requisições do Xano gratuito; com o backend indisponível, os cartões mostram "—" em vez de números inventados.
- No modo demonstração, os números vêm dos dados de demonstração.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `public-site`: números reais na página inicial.

## Impact

- **Backend:** novo endpoint público no grupo `assistencia-tech-os`.
- **Código:** modelo `PublicStats`, `PortalRepository.public_stats` (demonstração e Xano), serviço com cache, estado e página inicial.
- **Testes:** cálculo na demonstração, NPS, cache, indisponibilidade e adaptador Xano simulado.

## Out of Scope

- Gráficos públicos ou séries históricas.
