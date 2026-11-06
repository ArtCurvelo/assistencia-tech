# Assistência TECH — Reflex 1.0

Aplicação acadêmica de gestão de assistência técnica, desenvolvida em Python com Reflex, com backend planejado no Xano.

## Funcionalidades atuais
- Página inicial, serviços e consulta pública de OS (sem dados pessoais).
- Painel com indicadores: ordens em aberto, aguardando aprovação, prontas para entrega e valor a receber.
- Clientes: CPF e telefone validados, unicidade de CPF e e-mail, edição, exclusão controlada e histórico de atendimentos.
- Equipamentos: vínculo com cliente, número de série único, filtros, edição, exclusão controlada e histórico de manutenção.
- Ordens de serviço: fluxo de status com regras, técnico responsável, diagnóstico, orçamento de serviços e peças, pagamentos, cancelamento com motivo e linha do tempo.
- Formulários demonstrativos de login e cadastro (autenticação real em mudança futura).

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

## Testes
```powershell
python -m pytest
```

## Rotas
- `/`
- `/servicos`
- `/login`
- `/cadastro`
- `/admin`
- `/admin/clientes` e `/admin/clientes/[cliente_id]`
- `/admin/equipamentos`
- `/admin/ordens` e `/admin/ordens/[codigo]`

## Fonte de dados
A aplicação usa uma camada de acesso a dados com duas fontes, escolhidas por variável de ambiente (veja `.env.example` e `docs/XANO_INTEGRATION.md`):
- `demo` (padrão): dados fictícios em memória, sempre identificados como "Modo demonstração".
- `xano`: backend Xano. Até a documentação oficial da API ser fornecida, as operações informam que a integração está pendente, sem enviar requisições e sem recorrer aos dados de demonstração.

## Limitações conhecidas
- No modo demonstração, os registros ficam em memória no processo da aplicação; não existe persistência em banco.
- Login e cadastro não autenticam nem armazenam credenciais.
- A integração real com o Xano depende da documentação oficial da API (contratos ainda não fornecidos).

## Documentação
- `docs/PROJECT.md` — contexto e escopo.
- `docs/REQUIREMENTS.md` — requisitos funcionais e não funcionais.
- `docs/DATA_MODEL.md` — diagrama entidade-relacionamento e ciclo de vida da OS.
- `docs/OPEN_SPEC_APPROACH.md` — processo de especificação com OpenSpec.
- `docs/XANO_INTEGRATION.md` — arquitetura de dados, configuração e registro de contratos do Xano.
- `docs/CHANGELOG.md` — histórico de mudanças.
- `openspec/specs/` — especificações vigentes.
- `openspec/changes/` — mudanças em andamento (`integrate-xano-backend` e `expand-service-domain`).
