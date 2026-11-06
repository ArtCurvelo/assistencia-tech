# Assistência TECH — Reflex 1.0

Aplicação acadêmica de gestão de assistência técnica, desenvolvida em Python com Reflex, com backend planejado no Xano.

## Funcionalidades atuais
- Página inicial e página de serviços.
- Formulários demonstrativos de login e cadastro.
- Consulta de OS usando dados fictícios.
- Painel administrativo.
- Cadastro demonstrativo de clientes, equipamentos e ordens.
- Pesquisa e alteração de status das ordens.

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
- `/admin/clientes`
- `/admin/equipamentos`
- `/admin/ordens`

## Limitações conhecidas
- Os registros são fictícios e ficam no estado da aplicação; não existe persistência em banco.
- Login e cadastro não autenticam nem armazenam credenciais.
- Não há conexão com o Xano. Os contratos reais da API ainda precisam ser fornecidos antes da integração.

## Documentação
- `docs/PROJECT.md` — contexto e escopo.
- `docs/REQUIREMENTS.md` — requisitos funcionais e não funcionais.
- `docs/OPEN_SPEC_APPROACH.md` — processo de especificação com OpenSpec.
- `docs/CHANGELOG.md` — histórico de mudanças.
- `openspec/specs/` — especificações vigentes.
- `openspec/changes/` — mudanças em andamento (atualmente `integrate-xano-backend`).
