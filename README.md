# Assistência TECH — Reflex 1.0

Protótipo acadêmico de gestão de assistência técnica, baseado nos HTMLs e CSS fornecidos.

## Funcionalidades
- Página inicial e página de serviços.
- Formulários demonstrativos de login e cadastro.
- Consulta de OS usando dados fictícios.
- Painel administrativo.
- Cadastro demonstrativo de clientes, equipamentos e ordens.
- Pesquisa e alteração de status das ordens.

## Requisitos
- Python 3.10+ (recomenda-se Python 3.11 ou 3.12 para compatibilidade ampla).
- Acesso à internet na instalação inicial das dependências e para carregar a fonte Inter.

## Instalação
```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
reflex init
reflex run
```

Linux/macOS:
```bash
source .venv/bin/activate
pip install -r requirements.txt
reflex init
reflex run
```

Se `reflex init` perguntar sobre sobrescrever arquivos de configuração, mantenha a configuração deste projeto.

A aplicação normalmente abre em `http://localhost:3000`.

## Testes
```bash
python -m unittest discover -s tests -v
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
- Não há conexão com APIs externas. Os contratos reais ainda precisam ser inspecionados antes da integração.
- Este artefato é uma primeira implementação e precisa de validação em ambiente Reflex e inspeção visual em navegador antes de ser considerado pronto para produção.

## Documentação de especificação
Consulte `docs/PROJECT.md`, `docs/REQUIREMENTS.md`, `docs/DESIGN.md`, `docs/TASKS.md` e `docs/CHANGELOG.md`.
