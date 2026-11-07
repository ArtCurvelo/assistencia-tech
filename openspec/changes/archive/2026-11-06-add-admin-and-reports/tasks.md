# Tasks

## 1. Domínio

- [x] 1.1 Adicionar `staff.manage` e `reports.view` à matriz de permissões; verificar com os testes da matriz atualizados.
- [x] 1.2 Implementar `domain/staff_rules.py` (autodesativação, último administrador, técnico com ordens em aberto); verificar com testes de cada regra.
- [x] 1.3 Implementar `domain/reports.py` (volume, recebimentos por forma, ticket médio, produção por técnico, tempo médio) e `domain/csv_export.py`; verificar com testes sobre os dados de demonstração e um caso com `;` e aspas.

## 2. Dados e serviços

- [x] 2.1 Ampliar `AuthProvider` (listar, criar e atualizar contas) e `TechnicianRepository` (criar, atualizar, `active`), com adaptador Xano sem contrato; verificar com testes de contrato interno e o teste de nenhuma requisição sem contrato.
- [x] 2.2 Implementar `services/staff.py` (listar, cadastrar, editar, redefinir senha, desativar e reativar) com as regras e permissões; verificar com testes dos cenários da spec `staff-management`, incluindo a recusa de login e de sessão após desativação.
- [x] 2.3 Implementar `services/reports.py` (período padrão, validação do período, relatório e CSV) com permissões; verificar com testes dos cenários da spec `operational-reports`.
- [x] 2.4 Oferecer somente técnicos ativos para atribuição; verificar com teste do serviço de ordens e no navegador.

## 3. Interface

- [x] 3.1 Criar `/admin/colaboradores` (lista, cadastro, edição, senha provisória, desativação com confirmação); verificar no navegador como Administrador e o acesso negado como Atendente.
- [x] 3.2 Criar `/admin/relatorios` (período, indicadores, tabelas e exportação CSV); verificar no navegador como Administrador e Atendente, o acesso negado como Técnico e o arquivo baixado.
- [x] 3.3 Exibir "Relatórios" e "Colaboradores" no menu conforme a permissão; verificar no navegador com cada perfil.

## 4. Documentação e verificação

- [x] 4.1 Atualizar `DEMO_USERS.md` (matriz), `REQUIREMENTS.md`, `XANO_INTEGRATION.md`, `README.md` e `CHANGELOG.md`; verificar conferindo com as specs.
- [x] 4.2 Executar `pytest`, `openspec validate --all --strict` e a contagem de linhas, e registrar os resultados e as verificações no navegador neste arquivo.

## Registro de verificação (2026-11-06)

**Testes automatizados:** 312 aprovados, 0 falhas. Novos: `test_reports_domain` (regras de colaboradores, período inclusivo em horário de Brasília, relatório sobre o seed — 7 abertas, R$ 325,00 em PIX, ticket R$ 225,00, Diego 2/2 com R$ 436,00, Carlos 3/0 com R$ 1.835,00, tempo médio 2,3 dias —, CSV com BOM, `;` e aspas) e `test_staff_reports_services` (permissões, cadastro e recusas, técnico com ordens, promoção aplicada na próxima ação, último administrador, autodesativação, desativação revogando sessão e login, técnico inativo não atribuível, redefinição de senha, períodos inválidos). `test_xano` cobre 24 operações sem contrato. `openspec validate --all --strict`: 7 itens válidos. Maior arquivo Python: 347 linhas.

**Navegador (modo demonstração):**
- Administrador: menu com "Relatórios" e "Colaboradores"; lista com 5 colaboradores, sem clientes, "(você)" e sem "Desativar" na própria linha.
- Cadastro de técnico: especialidade habilitada ao escolher "Técnico"; e-mail em uso recusado mantendo os dados; "Bruno Alves" cadastrado e oferecido na atribuição de técnico da OS-2026-00126.
- Edição: mudar Carlos para Atendente recusado ("2 ordens em aberto").
- Desativação de Paulo Nunes com confirmação; a situação passa a "Inativo" e o login dele é recusado com "E-mail ou senha inválidos.".
- Técnico: menu sem "Relatórios" e "Colaboradores"; as duas páginas levam a `/acesso-negado`.
- Relatórios: período padrão de 08/08/2026 a 06/11/2026; indicadores e tabelas iguais aos testes; período invertido recusado; filtro de outubro atualizado; CSV baixado como `ordens-2026-10-01-a-2026-10-31.csv`, com BOM UTF-8 (`EF BB BF`), cabeçalho, 7 linhas, `;` e vírgula decimal.
- Celular (375 px): `/admin/relatorios` e `/admin/colaboradores` sem largura excedente.

- Reativação de Paulo Nunes pela interface (Inativo → Ativo) e login dele em seguida.
- Redefinição de senha da Fernanda: senha fraca recusada; nova senha aceita; a senha anterior passa a ser recusada no login.
- Atendente: menu com "Relatórios" e sem "Colaboradores"; `/admin/colaboradores` leva a `/acesso-negado`; `/admin/relatorios` exibe os indicadores e o botão "Exportar CSV".

**Observação:** durante a verificação, o servidor de desenvolvimento recarregou e os dados em memória voltaram ao seed (comportamento conhecido do modo demonstração); as verificações seguintes foram refeitas a partir desse estado.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
