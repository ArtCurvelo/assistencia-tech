# Tasks

## 1. Domínio

- [ ] 1.1 Adicionar `staff.manage` e `reports.view` à matriz de permissões; verificar com os testes da matriz atualizados.
- [ ] 1.2 Implementar `domain/staff_rules.py` (autodesativação, último administrador, técnico com ordens em aberto); verificar com testes de cada regra.
- [ ] 1.3 Implementar `domain/reports.py` (volume, recebimentos por forma, ticket médio, produção por técnico, tempo médio) e `domain/csv_export.py`; verificar com testes sobre os dados de demonstração e um caso com `;` e aspas.

## 2. Dados e serviços

- [ ] 2.1 Ampliar `AuthProvider` (listar, criar e atualizar contas) e `TechnicianRepository` (criar, atualizar, `active`), com adaptador Xano sem contrato; verificar com testes de contrato interno e o teste de nenhuma requisição sem contrato.
- [ ] 2.2 Implementar `services/staff.py` (listar, cadastrar, editar, redefinir senha, desativar e reativar) com as regras e permissões; verificar com testes dos cenários da spec `staff-management`, incluindo a recusa de login e de sessão após desativação.
- [ ] 2.3 Implementar `services/reports.py` (período padrão, validação do período, relatório e CSV) com permissões; verificar com testes dos cenários da spec `operational-reports`.
- [ ] 2.4 Oferecer somente técnicos ativos para atribuição; verificar com teste do serviço de ordens e no navegador.

## 3. Interface

- [ ] 3.1 Criar `/admin/colaboradores` (lista, cadastro, edição, senha provisória, desativação com confirmação); verificar no navegador como Administrador e o acesso negado como Atendente.
- [ ] 3.2 Criar `/admin/relatorios` (período, indicadores, tabelas e exportação CSV); verificar no navegador como Administrador e Atendente, o acesso negado como Técnico e o arquivo baixado.
- [ ] 3.3 Exibir "Relatórios" e "Colaboradores" no menu conforme a permissão; verificar no navegador com cada perfil.

## 4. Documentação e verificação

- [ ] 4.1 Atualizar `DEMO_USERS.md` (matriz), `REQUIREMENTS.md`, `XANO_INTEGRATION.md`, `README.md` e `CHANGELOG.md`; verificar conferindo com as specs.
- [ ] 4.2 Executar `pytest`, `openspec validate --all --strict` e a contagem de linhas, e registrar os resultados e as verificações no navegador neste arquivo.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
