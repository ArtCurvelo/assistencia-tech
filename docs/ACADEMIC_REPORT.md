# Relatório técnico — Assistência TECH

Curso de Análise e Desenvolvimento de Sistemas · Novembro de 2026

## 1. Introdução e objetivo

O Assistência TECH é uma aplicação web de gestão de assistência técnica. Ela cobre o atendimento ao cliente, o cadastro de equipamentos, o ciclo de vida da ordem de serviço (do recebimento à entrega), a gestão da equipe e os relatórios operacionais. O cliente tem um portal para acompanhar os próprios atendimentos.

O objetivo do trabalho é aplicar práticas de engenharia de software em um sistema completo e verificável: especificação antes da implementação, arquitetura em camadas, regras de negócio testáveis, controle de acesso e documentação rastreável.

## 2. Tecnologias

| Item | Escolha | Observação |
|---|---|---|
| Linguagem | Python 3.14 | Ambiente virtual `.venv` |
| Framework web | Reflex 0.8 | Interface e servidor em Python; tema escuro do Radix |
| Validação de dados | Pydantic 2 | Modelos imutáveis |
| HTTP | httpx | Cliente do Xano, testado com `MockTransport` |
| Gráficos | Recharts (via Reflex) | Painel administrativo |
| Testes | pytest, anyio, pytest-cov | Testes síncronos e assíncronos |
| Especificação | OpenSpec 1.14 (esquema `spec-driven`) | Propostas, requisitos, design e tarefas |
| Backend planejado | Xano | Integração preparada; contratos pendentes |

## 3. Requisitos

`docs/REQUIREMENTS.md` lista **32 requisitos funcionais** e **14 não funcionais**, cada um ligado à especificação que o detalha. As especificações do OpenSpec reúnem **12 capacidades**, **88 requisitos** e **141 cenários** no formato *WHEN/THEN*.

| Área | Capacidades |
|---|---|
| Interface | `design-system`, `responsive-interface` |
| Dados e integração | `data-source`, `backend-integration` |
| Domínio | `client-management`, `equipment-management`, `service-orders` |
| Acesso | `user-auth`, `access-control`, `customer-portal` |
| Administração | `staff-management`, `operational-reports` |

## 4. Metodologia

O desenvolvimento seguiu um processo orientado a especificações (OpenSpec), em fases incrementais. Cada fase foi uma mudança com quatro artefatos:

1. **Proposta:** motivação, escopo, premissas e o que fica fora.
2. **Specs:** requisitos com `SHALL/MUST` e cenários verificáveis.
3. **Design:** decisões técnicas com alternativas consideradas e riscos.
4. **Tarefas:** cada uma com sua forma de verificação e um registro final com testes executados, verificações no navegador e limitações.

| Fase | Mudança | Entrega |
|---|---|---|
| 0 | — | Repositório git, ambiente padronizado, correção do OpenSpec |
| 1 | `integrate-xano-backend` | Camada de dados, modo demonstração, cliente Xano sem contratos |
| 2 | `expand-service-domain` | Domínio completo de clientes, equipamentos e ordens |
| 3 | `add-auth-and-access-control` | Autenticação, perfis, permissões e portal do cliente |
| 4 | `refine-frontend-experience` | Responsividade, gráficos, acessibilidade e usabilidade |
| 5 | `add-admin-and-reports` | Gestão de colaboradores, relatórios e CSV |
| 7 | `prepare-academic-delivery` | Arquitetura, roteiro de demonstração e este relatório |

Tarefas sem evidência não são marcadas como concluídas. Por exemplo, duas tarefas de acessibilidade da fase 4 continuam abertas porque não puderam ser observadas visualmente.

## 5. Arquitetura

A aplicação é organizada em camadas, com dependências apontando para o domínio (detalhes e diagramas em `docs/ARCHITECTURE.md`):

- **Interface** (`pages/`, `components/`, `state/`): exibe dados, controla a sessão e faz a guarda das rotas.
- **Serviços de aplicação** (`services/`): orquestram cada operação e verificam as permissões.
- **Domínio** (`domain/`): regras puras, sem I/O, como validação, transições de status, valores, permissões, senhas e relatórios.
- **Dados** (`data/`): interfaces de repositório com duas implementações, o modo demonstração em memória e o adaptador Xano.

A regra que guiou a integração foi **nunca inventar contratos**. O adaptador Xano consulta um registro de contratos que permanece vazio até a documentação oficial; sem contrato, a operação falha com uma mensagem clara e nenhuma requisição é enviada. Isso é garantido por teste para as 24 operações internas.

## 6. Modelagem de dados

O modelo, com diagrama entidade-relacionamento e diagrama de estados em `docs/DATA_MODEL.md`, tem as entidades Cliente, Equipamento, Técnico, Conta de usuário e Ordem de Serviço. A ordem é um agregado com itens de orçamento, pagamentos e histórico.

- O ciclo da OS tem 7 status e transições definidas como dados, com pré-condições: técnico atribuído, diagnóstico, itens de orçamento, quitação antes da entrega e motivo para o cancelamento.
- Valores em `Decimal`, arredondados em centavos.
- O histórico é imutável e registra data, hora, autor (nome e perfil) e o status de destino.

## 7. Segurança e privacidade

- **Senhas:** PBKDF2-SHA256 com sal e 600.000 iterações.
- **Login:** mensagem genérica, tempo de resposta equalizado e bloqueio após 5 tentativas.
- **Sessão:** token opaco no servidor, com expiração por inatividade e revogação.
- **Permissões:** quatro perfis (Administrador, Atendente, Técnico e Cliente) com matriz verificada célula a célula. As permissões são aplicadas nos serviços e não apenas na interface, e o técnico só altera as próprias ordens.
- **Privacidade:** consulta pública sem dados pessoais; portal restrito às ordens do cliente, com CPF mascarado.
- **Configuração:** nenhuma credencial versionada; redirecionamento após o login aceita apenas caminhos internos.

## 8. Qualidade e métricas

Valores medidos em 06/11/2026 (registrados em `openspec/changes/archive/2026-11-06-prepare-academic-delivery/tasks.md`):

| Métrica | Valor |
|---|---|
| Testes automatizados | 313, todos aprovados |
| Cobertura das camadas testáveis (domínio, serviços, dados, modelos, apresentadores, configuração) | 97% |
| Cobertura total, incluindo páginas e estados Reflex | 69% |
| Arquivos Python da aplicação | 66 (5.421 linhas não vazias) |
| Arquivos de teste | 15 |
| Maior arquivo Python | 347 linhas (limite do projeto: 1.000) |
| Validação das especificações | `openspec validate --all --strict` sem erros |

A diferença entre as duas coberturas é intencional e está documentada: as páginas e os estados Reflex foram verificados no navegador em cada fase, nos modos demonstração e Xano, e a largura das páginas foi medida em 375 px e 768 px na fase 4. Essas verificações estão registradas nos `tasks.md`, mas não há testes automatizados de interface.

## 9. Limitações

- A integração real com o Xano depende da documentação oficial da API; até lá, a aplicação funciona no modo demonstração.
- No modo demonstração, dados, contas e sessões ficam em memória e se perdem ao reiniciar o servidor.
- O cookie de sessão não é `HttpOnly`, por limitação do Reflex; o risco é mitigado e documentado.
- Não há testes automatizados de interface (por exemplo, com Playwright).
- A verificação visual do foco de teclado ficou pendente, por limitação do ambiente de testes.

## 10. Trabalhos futuros

1. Registrar os contratos do Xano a partir da documentação oficial e implementar o mapeamento das respostas (grupo 6 de `integrate-xano-backend`).
2. Persistência real das sessões e trilha de auditoria das ações administrativas.
3. Testes de interface automatizados e testes de acessibilidade.
4. Recuperação de senha por e-mail e troca obrigatória da senha provisória.

## 11. Conclusão

O projeto entrega um sistema funcional de ponta a ponta (atendimento, técnico, financeiro, cliente e administração) apoiado por especificações rastreáveis, regras de negócio isoladas e testadas, controle de acesso aplicado no servidor e documentação que permite reproduzir e avaliar cada decisão. A integração com o backend foi preparada sem suposições, mantendo o sistema honesto sobre o que está e o que não está concluído.
