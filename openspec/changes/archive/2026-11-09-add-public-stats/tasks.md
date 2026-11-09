# Tasks

## 1. Backend e adaptadores

- [x] 1.1 Endpoint `GET /estatisticas_publicas` no XanoScript; validar pelo Developer MCP, simular e enviar após autorização.
- [x] 1.2 `PublicStats`, `PortalRepository.public_stats` na demonstração e no Xano; contrato-alvo; testes.

## 2. Aplicação

- [x] 2.1 Serviço com cache de 5 minutos e "—" em falha; cartões da página inicial; testes.

## 3. Verificação

- [x] 3.1 `pytest`, `openspec validate --strict`, verificador de contrato, chamada real ao endpoint e conferência no site publicado.

## Registro de verificação (2026-11-09)

- **pytest (.venv):** 452 passed (7 testes novos em `tests/test_public_stats.py`; a trava de rotas públicas em `tests/test_xano.py` passou a incluir `portal.public_stats`).
- **XanoScript:** 63 arquivos válidos no Developer MCP; simulação mostrou só `CREATE query estatisticas_publicas GET` (e a alteração recorrente da tabela `user`); envio após autorização.
- **Chamada real:** `GET /api:assistencia-tech-os/estatisticas_publicas` → 200 `{"entregues":1,"em_atendimento":1,"avaliacoes":1,"promotores":1,"detratores":0}`, sem token.
- **Verificador:** 36 de 36 endpoints.
- **Navegador (fonte Xano):** página inicial com "1 Equipamentos entregues", "1 Em atendimento agora", "+100 Satisfação (NPS) — NPS de 1 avaliação" e "90 dias Garantia".
