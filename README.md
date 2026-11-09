# Assistência TECH — Reflex 1.0

[![CI](https://github.com/ArtCurvelo/assistencia-tech/actions/workflows/ci.yml/badge.svg)](https://github.com/ArtCurvelo/assistencia-tech/actions/workflows/ci.yml)

Aplicação acadêmica de gestão de assistência técnica, desenvolvida em Python com Reflex, com backend planejado no Xano.

## Funcionalidades atuais
- Página inicial, serviços e consulta pública de OS (sem dados pessoais).
- Painel com indicadores: ordens em aberto, aguardando aprovação, prontas para entrega e valor a receber.
- Clientes: CPF e telefone validados, unicidade de CPF e e-mail, edição, exclusão controlada e histórico de atendimentos.
- Equipamentos: vínculo com cliente, número de série único, filtros, edição, exclusão controlada e histórico de manutenção.
- Ordens de serviço: fluxo de status com regras, técnico responsável, diagnóstico, orçamento de serviços e peças, pagamentos, cancelamento com motivo e linha do tempo.
- Login, logout e cadastro de cliente; perfis Administrador, Atendente, Técnico e Cliente com permissões aplicadas nas operações.
- Portal do cliente (`/minha-conta`) com as próprias ordens, orçamento e andamento.
- Gestão de colaboradores (cargos, senha provisória, desativação) e relatórios por período com exportação CSV.
- Aprovação ou recusa do orçamento pelo próprio cliente no portal.
- Estoque de peças: catálogo, entradas, movimentações, alerta de estoque baixo e baixa automática pelos orçamentos.
- Previsão de entrega, ordens atrasadas e garantia de 90 dias com abertura de ordem em garantia sem cobrança.
- Avaliação do atendimento (nota de 0 a 10) pelo cliente após a entrega, com NPS no painel e nos relatórios.
- Comprovante de entrada e de entrega para imprimir ou salvar em PDF, com QR code que abre a consulta pública da ordem (`/consulta/<código>`).

## Requisitos
- Python 3.14 (versão da `.venv` e da integração contínua; outras versões não foram testadas).
- Reflex 0.8.x (fixado em `requirements.txt`).
- Acesso à internet na instalação inicial das dependências e para carregar a fonte Inter.

> **Atenção:** execute sempre os comandos com a `.venv` ativada. O Python global desta máquina tem outra versão do Reflex (0.10), incompatível com a faixa fixada no projeto.

## Instalação (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
reflex run
```

Linux/macOS:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
reflex run
```

A aplicação normalmente abre em `http://localhost:3000`.

## Acesso de demonstração
Na tela `/login`, use o bloco **Acesso rápido** para entrar como Administrador, Atendente, Técnico ou Cliente. As contas e senhas de teste estão em `docs/DEMO_USERS.md`.

## Testes
```powershell
python -m pytest
python -m pytest --cov=assistencia_tech   # cobertura (pytest-cov)
```

## Integração contínua
O workflow `.github/workflows/ci.yml` roda no GitHub Actions a cada `push` e `pull_request`, sem segredos e sem acessar o Xano real:
- **Testes (Python 3.14):** `pytest` com cobertura, verificador de contrato com as cópias de `docs/xano-openapi/` (`--offline`) e montagem de todas as páginas do Reflex.
- **Especificações:** `openspec validate --all --strict`.

Os testes também conferem regras do projeto: arquivos Python com menos de 1.000 linhas, nenhum `.env` versionado e nenhum token JWT nos arquivos versionados (`tests/test_project_rules.py`).

## Rotas
Públicas: `/`, `/servicos`, `/consulta/[codigo]`, `/login`, `/cadastro`, `/acesso-negado`. Cliente: `/minha-conta`, `/minha-conta/ordens/[codigo]` e `/minha-conta/ordens/[codigo]/comprovante`. Administração (exige login):

- `/`
- `/servicos`
- `/login`
- `/cadastro`
- `/admin`
- `/admin/clientes` e `/admin/clientes/[cliente_id]`
- `/admin/equipamentos`
- `/admin/ordens`, `/admin/ordens/[codigo]` e `/admin/ordens/[codigo]/comprovante`
- `/admin/estoque`
- `/admin/relatorios` (Administrador e Atendente)
- `/admin/colaboradores` (Administrador)

## Fonte de dados
A aplicação usa uma camada de acesso a dados com duas fontes, escolhidas por variável de ambiente (veja `.env.example` e `docs/XANO_INTEGRATION.md`):
- `demo` (padrão): dados fictícios em memória, sempre identificados como "Modo demonstração".
- `xano`: backend Xano (pasta `xano/`, em XanoScript), sem recorrer aos dados de demonstração quando indisponível.

O QR code dos comprovantes aponta para `ASSISTENCIA_PUBLIC_URL` (por exemplo, o domínio do site publicado). Sem essa variável, usa o endereço pelo qual o sistema foi aberto; com `localhost`, o QR code só funciona no próprio computador.

## Limitações conhecidas
- No modo demonstração, os registros ficam em memória no processo da aplicação; não existe persistência em banco.
- Contas, sessões e bloqueios de login ficam em memória no modo demonstração e se perdem ao reiniciar o servidor.
- O PDF do comprovante é gerado pela impressão do navegador ("Salvar como PDF"), não pelo servidor.

## Documentação
- `docs/XANO_DEV_ENV.md` — Xano CLI, Developer MCP e fluxo de sincronização do backend.
- `docs/XANO_AI_PROMPTS.md` — prompts em etapas para a IA do Xano criar o backend conforme o contrato.
- `docs/XANO_BACKEND_SPEC.md` — ajustes a fazer no Xano (contrato-alvo); verifique com `python -m tools.xano_contract_check`.
- `docs/XANO_CONTRACT_ANALYSIS.md` — análise da documentação atual do Xano.
- `docs/ACADEMIC_REPORT.md` — relatório técnico (requisitos, metodologia, arquitetura, segurança, métricas e limitações).
- `docs/ARCHITECTURE.md` — camadas, fluxo de uma operação, decisões e estratégia de testes.
- `docs/DEMO_SCRIPT.md` — roteiro de demonstração (≈ 15 min), automatizado em `tests/test_demo_script.py`.
- `docs/PROJECT.md` — contexto e escopo.
- `docs/REQUIREMENTS.md` — requisitos funcionais e não funcionais.
- `docs/DATA_MODEL.md` — diagrama entidade-relacionamento e ciclo de vida da OS.
- `docs/DEMO_USERS.md` — contas de demonstração (senhas de teste) e matriz de permissões.
- `docs/OPEN_SPEC_APPROACH.md` — processo de especificação com OpenSpec.
- `docs/XANO_INTEGRATION.md` — arquitetura de dados, configuração e registro de contratos do Xano.
- `docs/CHANGELOG.md` — histórico de mudanças.
- `openspec/specs/` — especificações vigentes.
- `openspec/changes/` — mudanças em andamento (veja o estado de cada uma em `docs/OPEN_SPEC_APPROACH.md`).
