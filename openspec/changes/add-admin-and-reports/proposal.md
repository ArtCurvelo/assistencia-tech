# Proposal: Gestão de colaboradores e relatórios operacionais

## Why

As contas de colaboradores existem apenas nos dados de demonstração: não há como cadastrar um novo técnico, mudar o cargo de alguém ou desativar o acesso de quem saiu da empresa. A administração também não tem visão consolidada da operação por período (produção por técnico, faturamento recebido, tempo de reparo), algo esperado de um sistema de gestão e central para a demonstração acadêmica.

## What Changes

- **Colaboradores** (`/admin/colaboradores`, somente Administrador): listar, cadastrar com senha provisória, editar nome, cargo e especialidade, redefinir a senha, desativar e reativar o acesso.
- **Regras de segurança da gestão:** e-mail único entre contas; o administrador não pode desativar a si mesmo; deve sempre existir ao menos um administrador ativo; desativar revoga o acesso imediatamente; um técnico com ordens em aberto não pode deixar o cargo de Técnico.
- **Técnicos vinculados:** cadastrar um colaborador Técnico cria o técnico usado nas ordens; técnicos inativos deixam de ser oferecidos para novas atribuições, mas continuam no histórico.
- **Relatórios** (`/admin/relatorios`, Administrador e Atendente) por período: volume de ordens abertas, entregues e canceladas; valor recebido por forma de pagamento; produção por técnico; tempo médio entre a abertura e a conclusão; ticket médio.
- **Exportação CSV** das ordens do período, compatível com planilhas em português (separador `;`, vírgula decimal, UTF-8 com BOM).
- **Permissões novas:** `staff.manage` (Administrador) e `reports.view` (Administrador e Atendente).

## Capabilities

### New Capabilities

- `staff-management`: cadastro e manutenção de colaboradores, cargos, senhas provisórias e ativação de acesso.
- `operational-reports`: indicadores operacionais e financeiros por período e exportação CSV.

### Modified Capabilities

- Nenhuma especificação vigente em `openspec/specs/` muda. As novas permissões complementam a matriz da mudança ainda não arquivada `add-auth-and-access-control`, sem alterar as permissões existentes.

## Impact

- **Código:** `domain/permissions.py` (novas permissões), `domain/staff_rules.py` e `domain/reports.py` (regras puras), `AuthProvider` com listagem, criação e atualização de contas, `TechnicianRepository` com criação e atualização, `services/staff.py` e `services/reports.py`, páginas e estados de colaboradores e relatórios, item de menu por permissão.
- **Xano:** novas operações internas (`users.*`, `technicians.create`, `technicians.update`) sem contrato registrado.
- **Testes:** regras de gestão (último administrador, autodesativação, técnico com ordens), cálculos dos relatórios com dados conhecidos, formato do CSV e permissões.

## Assumptions

- O período padrão dos relatórios é de 90 dias até a data atual, ajustável pelo usuário.
- A senha provisória segue a política de senha existente; não há troca obrigatória no primeiro acesso nesta mudança.
- O tempo de reparo é medido da abertura até o primeiro evento de mudança para Concluído.
- O ticket médio é a média do valor total das ordens entregues no período.

## Out of Scope

- Edição da matriz de permissões pela interface (os cargos são fixos).
- Troca obrigatória de senha, recuperação de senha por e-mail e trilha de auditoria de ações administrativas fora da OS.
- Gráficos adicionais nos relatórios além das tabelas e indicadores.
