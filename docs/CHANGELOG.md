# Changelog

## Não lançado — Incrementos e publicação (2026-11-07 a 2026-11-13)
Cada item é uma mudança OpenSpec arquivada em `openspec/changes/archive/`, com o registro do que foi testado.
- **Backend próprio no Xano** em XanoScript (`xano/`), integrado à aplicação; verificador de contrato com todos os endpoints atendidos.
- **Aprovação do orçamento pelo cliente** no portal (`add-client-budget-approval`).
- **Estoque de peças** com baixa e devolução pelos orçamentos (`add-parts-inventory`).
- **Previsão de entrega, atrasos e garantia de 90 dias** (`add-deadlines-and-warranty`).
- **Comprovante com QR code** e consulta pública por link (`add-order-receipt`).
- **Avaliação do atendimento e NPS** (`add-service-rating`).
- **Integração contínua** no GitHub Actions (`add-continuous-integration`) e **testes de ponta a ponta** no navegador (`add-e2e-tests`).
- **Publicação** no Render com Docker (`add-public-deployment`).
- **Página de serviços, painel orientado a ações** e **números reais na página inicial** (`improve-services-and-dashboard`, `add-public-stats`).
- **Quadro Kanban** (`add-orders-board`) e **evolução mensal e PDF** nos relatórios (`improve-reports`).
- **LGPD no portal:** exportação e exclusão de dados pelo titular (`add-lgpd-portal`).
- Logo, campos de texto e espaçamentos corrigidos; povoamento de vitrine (`tools/seed_showcase.py`); documentação nova (`VISAO_DO_SISTEMA.md`, `MANUAL.md`, `ROTEIRO_APRESENTACAO.md`).

## Não lançado — Contrato do Xano (2026-11-07)
- Documentação OpenAPI dos grupos de Autenticação, Cliente e Ordens de Serviço registrada em `docs/xano-openapi/` (grupo Sistema de Gestão: acesso restrito, HTTP 403).
- Análise de compatibilidade (`XANO_CONTRACT_ANALYSIS.md`) e especificação dos ajustes no Xano (`XANO_BACKEND_SPEC.md`), conforme a opção A.
- Verificador automático do contrato (`python -m tools.xano_contract_check`) com testes; situação atual: 1 de 27 endpoints atendidos.
- Cliente Xano com validação TLS pelo repositório de certificados do sistema (`truststore`).

## Não lançado — Arquivamento no OpenSpec (2026-11-06)
- Arquivadas `expand-service-domain`, `add-auth-and-access-control`, `add-admin-and-reports` e `prepare-academic-delivery`; 62 requisitos incorporados às especificações vigentes (10 capacidades).
- Mantidas abertas `refine-frontend-experience` (2 verificações pendentes) e `integrate-xano-backend` (contratos do Xano pendentes).

## Não lançado — Fase 7 (entrega acadêmica, mudança `prepare-academic-delivery`)
- `ARCHITECTURE.md`, `DEMO_SCRIPT.md` e `ACADEMIC_REPORT.md`; roteiro automatizado em `tests/test_demo_script.py`.
- Cobertura medida com `pytest-cov`: 97% nas camadas testáveis e 69% no total.
- Revisão de `README.md`, `PROJECT.md` e `OPEN_SPEC_APPROACH.md`.
- 313 testes automatizados.

## Não lançado — Fase 5 (administração, mudança `add-admin-and-reports`)
- Gestão de colaboradores: cadastro com senha provisória, edição de cargo e especialidade, redefinição de senha, desativação e reativação.
- Regras: e-mail único, sem autodesativação, sempre um administrador ativo, técnico com ordens em aberto não muda de cargo nem é desativado; técnicos inativos fora das novas atribuições.
- Relatórios por período (volume, recebimentos por forma, ticket médio, produção por técnico, tempo médio de reparo) e exportação CSV (`;`, vírgula decimal, UTF-8 com BOM).
- Permissões `staff.manage` (Administrador) e `reports.view` (Administrador e Atendente); itens de menu conforme a permissão.
- Eventos de status do histórico com o status de destino estruturado (`to_status`).
- 312 testes automatizados.

## Não lançado — Fase 4 (frontend e responsividade, mudança `refine-frontend-experience`)
- Correção da largura excedente no celular em clientes, equipamentos, ordens e detalhes (de até 754 px para 375 px): tabelas com rolagem própria.
- Menu administrativo recolhível abaixo de 900 px, com `aria-expanded`; barra lateral mantida no computador.
- Painel com gráficos Recharts (ordens por status e situação dos pagamentos) e indicadores em grade adaptável; "—" quando os dados não estão disponíveis.
- Formulários preservam os dados quando a operação é recusada e são limpos após o sucesso.
- Botão "Entrar" visível no celular; link "Pular para o conteúdo" e foco visível; página "Página não encontrada".
- 270 testes automatizados.

## Não lançado — Fase 3 (autenticação e acesso, mudança `add-auth-and-access-control`)
- Login e logout com sessão no servidor (token opaco em cookie `SameSite=Strict`, expiração após 2 h sem atividade).
- Senhas com PBKDF2-SHA256 e sal; política de senha; bloqueio de 5 minutos após 5 tentativas; mensagem genérica de credenciais inválidas.
- Cadastro de cliente com conta de acesso e entrada automática no portal.
- Perfis Administrador, Atendente, Técnico e Cliente; matriz de permissões em `domain/permissions.py`, aplicada nos serviços e na interface; escopo do técnico às próprias ordens; permissões por transição de status.
- Proteção de todas as rotas `/admin`, retorno seguro à página pretendida e página de acesso negado.
- Portal do cliente (`/minha-conta`) com as próprias ordens, sem dados internos.
- Histórico da OS com o nome e o perfil do autor real.
- Contas de demonstração com acesso rápido no login (somente no modo demonstração) e `docs/DEMO_USERS.md`.
- 268 testes automatizados.

## Não lançado — Fase 2 (domínio completo, mudança `expand-service-domain`)
- Regras de negócio em funções puras (`domain/`): validação de CPF, telefone e reais; fluxo de status com transições e pré-condições; cálculo de valores; histórico imutável.
- Serviços de aplicação (`services/`) para clientes, equipamentos e ordens; repositórios restritos à persistência.
- Novo modelo: vínculos por identificador, técnicos, itens de orçamento, pagamentos e eventos de histórico; ordem de serviço como agregado.
- Dados de demonstração reconstruídos com as próprias regras do domínio (6 clientes, 3 técnicos, 8 equipamentos, uma OS em cada status).
- Interface reorganizada em `pages/`, `components/` e `state/` (subestados); páginas de detalhe do cliente e da OS; diálogos de edição e confirmação; filtros; tema escuro do Radix.
- Consulta pública restrita a código, status, equipamento e última atualização.
- Documentação: `DATA_MODEL.md` (ER e diagrama de estados) e `REQUIREMENTS.md` rastreável às specs.
- 146 testes automatizados.

## Não lançado — Fase 1 (camada de dados, mudança `integrate-xano-backend`)
- Camada de acesso a dados com interfaces internas (`DataGateway`) e modo demonstração em memória.
- Seleção da fonte de dados por variáveis de ambiente (`.env.example`); modo Xano nunca recorre aos dados fictícios.
- Modelos Pydantic com validação e mensagens em português; hierarquia de erros com mensagens seguras ao usuário.
- Cliente HTTP do Xano com tempo limite e tradução de status HTTP; registro de contratos vazio até a documentação oficial.
- Interface: selo da fonte de dados ativa, alerta de falha de carregamento, mensagens e toasts de sucesso/erro, botões com estado de carregamento, estados vazios no painel e em equipamentos.
- Correções: código de OS agora sempre `OS-AAAA-NNNNN` (antes gerava `OS-2026-126`); card "Ordens em andamento" exibia o nome interno da variável; formulários inválidos não davam retorno ao usuário.
- 53 novos testes automatizados (56 no total).

## Não lançado — Fase 0 (fundação)
- Repositório git inicializado com snapshot do estado anterior.
- Versão do Reflex alinhada à `.venv` (0.8.28); `httpx` declarado; `pytest` em `requirements-dev.txt`.
- OpenSpec: spec `design-system` renomeada para `spec.md` e convertida ao formato de especificação vigente; spec `responsive-interface` sincronizada a partir da mudança arquivada; contexto do projeto definido em `openspec/config.yaml`.
- Mudança `integrate-xano-backend` planejada (proposta, specs, design e tarefas) e validada com `--strict`.
- Documentação corrigida: o projeto utiliza a CLI OpenSpec; referências do README a arquivos inexistentes removidas.

## 1.0.0 — protótipo demonstrativo
- Reconstruídas as páginas públicas de início, serviços, login e cadastro em Reflex.
- Criado painel administrativo com visão geral, clientes, equipamentos e ordens de serviço.
- Adicionada consulta demonstrativa de OS, busca e atualização de status.
- Preservada a paleta visual original.
- Documentadas limitações de autenticação, persistência e APIs.
