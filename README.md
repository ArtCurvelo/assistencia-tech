# Assistência TECH — Reflex 1.0

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

## Requisitos
- Python 3.10+ (a `.venv` do projeto usa Python 3.14).
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

## Rotas
Públicas: `/`, `/servicos`, `/login`, `/cadastro`, `/acesso-negado`. Cliente: `/minha-conta` e `/minha-conta/ordens/[codigo]`. Administração (exige login):

- `/`
- `/servicos`
- `/login`
- `/cadastro`
- `/admin`
- `/admin/clientes` e `/admin/clientes/[cliente_id]`
- `/admin/equipamentos`
- `/admin/ordens` e `/admin/ordens/[codigo]`
- `/admin/relatorios` (Administrador e Atendente)
- `/admin/colaboradores` (Administrador)

## Fonte de dados
A aplicação usa uma camada de acesso a dados com duas fontes, escolhidas por variável de ambiente (veja `.env.example` e `docs/XANO_INTEGRATION.md`):
- `demo` (padrão): dados fictícios em memória, sempre identificados como "Modo demonstração".
- `xano`: backend Xano. Até a documentação oficial da API ser fornecida, as operações informam que a integração está pendente, sem enviar requisições e sem recorrer aos dados de demonstração.

## Limitações conhecidas
- No modo demonstração, os registros ficam em memória no processo da aplicação; não existe persistência em banco.
- Contas, sessões e bloqueios de login ficam em memória no modo demonstração e se perdem ao reiniciar o servidor.
- A integração real com o Xano depende da documentação oficial da API (contratos ainda não fornecidos).

## Documentação
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
