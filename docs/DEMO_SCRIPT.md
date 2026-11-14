# Roteiro de demonstração (≈ 15 minutos)

> Roteiro do **modo demonstração local**. Para apresentar o site publicado com o Xano, use `ROTEIRO_APRESENTACAO.md`.

Roteiro para apresentar o Assistência TECH ao professor. Os passos 1 a 9 são executados automaticamente pelos serviços em `tests/test_demo_script.py`; se esse teste passa, o roteiro funciona com os dados de demonstração.

## Preparação (antes da apresentação)

1. Ative o ambiente e confira os testes:
   ```powershell
   .venv\Scripts\Activate.ps1
   python -m pytest
   python -m pytest tests/test_demo_script.py -v
   ```
2. Inicie a aplicação **no modo demonstração** (padrão) e aguarde a compilação:
   ```powershell
   reflex run
   ```
3. Abra `http://localhost:3000` em uma janela anônima (sem sessões antigas). Deixe também uma aba com as DevTools no modo celular (375 px) para o passo 10.
4. Tenha em mãos `docs/DEMO_USERS.md` (contas e senhas de teste).

> Os dados ficam em memória: reiniciar o servidor volta ao estado inicial. Não altere código durante a apresentação, porque o recarregamento automático também reinicia os dados.

> **Datas:** o seed tem ordens de outubro de 2026. O código da nova OS usa o ano corrente (em 2026, `OS-2026-00127`; em 2027, `OS-2027-00001`), e o período padrão dos relatórios cobre os últimos 90 dias. Se a apresentação for depois de janeiro de 2027, ajuste o período do relatório para incluir outubro de 2026. Os valores citados (R$ 655,00 recebidos) consideram o seed mais os pagamentos feitos no passo 6.

## Roteiro

| # | Tempo | Perfil | Ação | O que destacar |
|---|---|---|---|---|
| 1 | 1 min | Visitante | Na página inicial, consulte `OS-2026-00125` em "Acompanhe seu equipamento". | Consulta pública mostra só status, equipamento e data; nenhum dado pessoal (projeção `PublicOrderView`). |
| 2 | 1 min | Visitante | Abra `/admin/clientes`. Em seguida, no login, tente `admin@assistencia.test` com a senha `errada123`. | Rotas protegidas redirecionam ao login com retorno à página; mensagem genérica que não revela se o e-mail existe. |
| 3 | 1,5 min | Cliente | Em "Criar conta", cadastre **Joana Teixeira**, CPF `529.982.247-25`, e-mail `joana@exemplo.test`, telefone `(21) 99876-5432`, senha `joana2026` (confirmação igual). Mostre antes um CPF inválido (`123.456.789-00`). Saia em seguida. | Validação de CPF por dígito verificador; senha com hash PBKDF2; cliente e conta criados juntos; portal vazio. |
| 4 | 2 min | Atendente (acesso rápido) | Em Equipamentos, cadastre para Joana um **Notebook Dell Inspiron 15**, série `DL-INS-2026`. Em Ordens, abra a OS (problema "Não liga após queda de energia"): será a **OS-2026-00127**. No detalhe, atribua **Carlos Mendes**. | Equipamento vinculado ao cliente; código sequencial; o atendente não vê o formulário de diagnóstico (permissão). |
| 5 | 2,5 min | Técnico (acesso rápido: Carlos) | Na OS-2026-00127: mova para Em análise; tente "Aguardando aprovação" (recusado: falta diagnóstico); registre "Fonte de alimentação queimada."; adicione Serviço "Troca da fonte" R$ 150,00 e Peça "Fonte 65 W" 1 × R$ 180,00; envie para aprovação. Abra a **OS-2026-00124** (da Fernanda). | Pré-condições das transições; total calculado (R$ 330,00); seletor mostra só os status permitidos ao perfil; somente consulta na ordem de outro técnico. |
| 6 | 2 min | Atendente → Técnico → Atendente | Atendente: "Mover para Em reparo" (aprovação). Técnico: "Mover para Concluído". Atendente: pagamento de R$ 130,00 em PIX; tente "Entregue" (recusado: saldo de R$ 200,00); pagamento de R$ 200,00 em cartão de crédito; "Mover para Entregue". | Separação de responsabilidades por cargo; entrega condicionada à quitação; linha do tempo com autor e perfil em cada evento. |
| 7 | 1 min | Cliente (Joana) | Entre como Joana e abra "Minha conta". | Portal com a própria OS entregue, orçamento, pagamentos e andamento; CPF mascarado; sem autores internos. |
| 8 | 1,5 min | Administrador (acesso rápido) | Painel: gráficos por status e pagamentos. Relatórios: período padrão; mostre recebimentos (R$ 655,00) e produção por técnico; clique em "Exportar CSV" e abra no Excel. | Indicadores calculados por funções puras testadas; CSV com `;`, vírgula decimal e acentos corretos. |
| 9 | 1 min | Administrador | Colaboradores: tente desativar Carlos (recusado: ordens em aberto); cadastre **Bruno Alves**, Técnico, "Impressoras", senha `bruno2026`. | Regras de proteção da gestão; o novo técnico fica disponível para atribuição. |
| 10 | 1 min | Qualquer | Mostre o painel em 375 px: barra superior, menu recolhível, tabelas com rolagem própria. | Responsividade medida (nenhuma página excede a largura da tela). |
| 11 | 1,5 min | — | No terminal: `python -m pytest`; `openspec list`; `openspec list --specs`; abra `openspec/specs/access-control/spec.md` e o registro de verificação em `openspec/changes/archive/2026-11-06-add-auth-and-access-control/tasks.md`. | Testes automatizados; processo spec-driven: especificações vigentes, mudanças arquivadas e registro de verificação. |

## Plano de contingência

- **Servidor não inicia ou cai:** mostre o passo 11 (`pytest`, incluindo `tests/test_demo_script.py -v`) e os documentos `ARCHITECTURE.md` e `DATA_MODEL.md`; reinicie com `reflex run` em paralelo.
- **Dados alterados por engano:** reinicie o servidor (os dados voltam ao seed). Os códigos do roteiro dependem do estado inicial.
- **Acesso rápido indisponível:** use as contas e senhas de `docs/DEMO_USERS.md`.
- **Bloqueio por tentativas no passo 2:** o bloqueio dura 5 minutos e só afeta o e-mail usado; use o acesso rápido de outro perfil.

## Mensagens-chave para a apresentação

1. **Engenharia antes do código:** cada fase começou com proposta, requisitos com cenários, design com alternativas e tarefas verificáveis (OpenSpec).
2. **Regras no lugar certo:** o domínio é puro e testado; a interface só exibe; o servidor decide.
3. **Segurança real:** hash de senha, sessão revogável, permissões verificadas no servidor, privacidade na consulta pública e no portal.
4. **Honestidade técnica:** a integração com o Xano está preparada, mas nenhum contrato foi inventado; operações sem contrato falham de forma explícita.
