# Tasks

## 1. Contenção e grade responsiva

- [x] 1.1 Conter painéis e tabelas na largura da coluna (CSS); verificar no navegador em 375 px que `/admin/clientes`, `/admin/clientes/4`, `/admin/equipamentos`, `/admin/ordens` e `/admin/ordens/OS-2026-00125` têm largura de página igual à da tela.
- [x] 1.2 Tornar a grade de indicadores adaptável (2/4 colunas) com valores sem quebra; verificar no navegador em 375 px e 1366 px.

## 2. Navegação

- [x] 2.1 Implementar o menu administrativo recolhível abaixo de 900 px, com `aria-expanded` e fechamento ao escolher uma página; verificar no navegador em 375 px, 768 px e 1366 px.
- [x] 2.2 Manter "Entrar" visível para visitantes no cabeçalho público do celular; verificar no navegador em 375 px.
- [x] 2.3 Adicionar o link "Pular para o conteúdo" e o foco visível; verificar com Tab no navegador.

## 3. Painel

- [x] 3.1 Criar `payment_summary` e adicionar cores e quantidades numéricas a `status_counts`, com testes em `tests/test_presenters.py`; verificar com `pytest`.
- [x] 3.2 Substituir as barras do painel por gráficos Recharts (status e pagamentos); verificar no navegador que todos os status e situações aparecem com quantidades.
- [x] 3.3 Exibir "—" nos indicadores antes do carregamento e quando ele falhar; verificar com teste de `EMPTY_METRICS` e no navegador observando o estado inicial do painel.

## 4. Formulários e páginas

- [x] 4.1 Preservar os dados de formulários recusados e limpar após o sucesso (clientes, equipamentos, abertura de OS, itens e pagamentos); verificar no navegador com um cadastro recusado e outro aceito.
- [x] 4.2 Criar a página "Página não encontrada"; verificar no navegador com uma rota inexistente.

## 5. Verificação integrada

- [x] 5.1 Executar `pytest`, `openspec validate --all --strict` e a contagem de linhas, e registrar os resultados neste arquivo.
- [x] 5.2 Percorrer as páginas públicas, administrativas e do portal em 375 px, 768 px e 1366 px, registrando a largura da página e as capturas de tela verificadas neste arquivo.

## Registro de verificação (2026-11-06)

**Testes automatizados:** 270 aprovados, 0 falhas (novos: dados dos gráficos, resumo de pagamentos e `EMPTY_METRICS`). `openspec validate --all --strict`: 6 itens válidos. Maior arquivo Python: 305 linhas (`presenters.py`). Compilação completa do frontend (`reflex export --frontend-only`) sem erros.

**Largura da página (`scrollWidth`) medida no navegador:**

| Página | Antes (375 px) | Depois (375 px) | Depois (768 px) |
|---|---|---|---|
| `/` e `/servicos` | 375 | 375 | — |
| `/admin` | 375 | 375 | 768 |
| `/admin/clientes` | 665 | 375 | 768 |
| `/admin/clientes/4` | 697 | 375 | — |
| `/admin/equipamentos` | 700 | 375 | — |
| `/admin/ordens` | 754 | 375 | 768 |
| `/admin/ordens/OS-2026-00125` | 545 | 375 | 768 |
| `/minha-conta` e detalhe da ordem | — | 375 | — |
| rota inexistente (404) | — | 375 | — |

**Navegador — verificações:**
- Celular (375 px): barra superior com marca e botão de menu; o título "Visão geral" aparece na primeira tela; o menu abre com as 4 páginas, o nome, o perfil e "Sair" (`aria-expanded` passa de `false` a `true`, rótulo "Abrir menu"/"Fechar menu") e fecha ao escolher "Clientes".
- Indicadores em 2 colunas no celular e 4 no computador; "R$ 706,00" em uma linha.
- Computador (1366 px): barra lateral fixa, gráfico de barras com as 7 situações em cores sólidas e gráfico de pagamentos (Pendente, Parcial, Pago) com legenda; captura de tela conferida.
- Visitante no celular: botão "Entrar" visível no cabeçalho.
- Formulário de clientes: cadastro recusado (CPF repetido) manteve nome, CPF, e-mail e telefone; cadastro aceito limpou os campos.
- `/admin/relatorio-inexistente`: página "Página não encontrada" com "Ir para a minha área" para usuário autenticado.
- Link "Pular para o conteúdo": é o primeiro elemento focável e aponta para `#conteudo` (que existe, com `tabindex=-1`).

**Não verificado visualmente / observações (tarefas 2.3 e 3.3 permanecem abertas por isso):**
- O deslocamento do link de salto e o contorno de foco (`:focus`, `:focus-visible`) não puderam ser observados, porque o painel do navegador estava oculto e a janela não tinha foco (`document.hasFocus() = false`); as regras CSS estão presentes e o elemento recebe o foco.
- 3.3: no modo Xano, o login (sem contrato) bloqueia o acesso antes do painel, então o cenário original "painel com a fonte Xano" deixou de ser alcançável desde a mudança de autenticação; o cenário foi reescrito para falha de carregamento e estado inicial. A cobertura é feita pelo teste de `EMPTY_METRICS` e pelo valor inicial do estado; o estado inicial é transitório e não foi capturado no navegador.
- Tablet (768 px) verificado por medição de largura, sem captura de tela.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.

## Fechamento das tarefas 2.3 e 3.3 (2026-11-13)

Conferidas por testes de ponta a ponta num navegador real (`e2e/test_site.py`, Chromium via Playwright):
- **2.3:** na página inicial, o primeiro Tab leva o foco a "Pular para o conteúdo", que entra na tela; o Tab seguinte mostra contorno de foco (`test_keyboard_reaches_the_skip_link_with_visible_focus`).
- **3.3:** a página do painel entregue pelo servidor, antes do carregamento dos dados, traz "—" em todos os indicadores (`test_dashboard_starts_with_dashes_before_loading`); a falha de carregamento continua coberta pelo teste de `EMPTY_METRICS`.
