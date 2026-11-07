# Design: Gestão de colaboradores e relatórios operacionais

## Context

Motivação em `proposal.md`; comportamento em `specs/staff-management` e `specs/operational-reports`.

Estado atual (commit `b4eb06f`): `UserAccount` (com `active`) fica no `DemoAuthProvider`, que só autentica, consulta e cadastra clientes; `Technician` não tem situação ativa; `AuthService.resolve` já recusa contas inativas e revoga a sessão; as permissões são uma matriz em `domain/permissions.py`.

## Decisions

### D1. Contas de colaboradores no `AuthProvider`

O `AuthProvider` ganha `list_users()`, `create_user(UserAccount sem id, senha)` e `update_user(UserAccount, nova_senha | None)`. As credenciais continuam encapsuladas no provedor: o hash é calculado dentro dele, e o serviço nunca manipula hashes. O `TechnicianRepository` ganha `create` e `update`, e `Technician` ganha `active: bool = True`.

- *Alternativa:* um `UserRepository` separado. Rejeitada para não espalhar credenciais em dois componentes.

### D2. Regras puras de gestão

`domain/staff_rules.py` concentra as regras sem I/O:

- `ensure_not_self(actor, target, action)`
- `ensure_admin_remains(users, target_id, new_role, new_active)`, que simula a mudança e exige ao menos um administrador ativo
- `ensure_technician_can_leave(open_orders_count)`

O serviço reúne os dados e chama essas funções.

### D3. Técnico vinculado à conta

Ao cadastrar um colaborador Técnico, o serviço cria o `Technician` (nome e especialidade) e grava `technician_id` na conta. A edição sincroniza nome e especialidade, e a desativação marca o técnico como inativo. Se a conta deixa de ser Técnico (permitido só sem ordens em aberto), o técnico fica inativo. Se volta a ser Técnico, o mesmo técnico é reativado. A lista de técnicos para atribuição passa a filtrar `active`, enquanto o catálogo completo continua disponível para nomes no histórico.

### D4. Revogação imediata

Nenhum mecanismo novo é necessário: `AuthService.resolve` já trata `active=False` como sessão inválida e revoga o token. A mudança de cargo também vale na próxima ação, porque o `Principal` é reconstruído a partir da conta a cada `resolve`.

### D5. Relatórios como funções puras

`domain/reports.py` recebe ordens, técnicos e o período (`date_from`, `date_to`) e devolve dataclasses imutáveis (`VolumeReport`, `RevenueReport`, `TechnicianRow`, `TurnaroundReport`). Os critérios são:

- **Volume:** ordens abertas no período.
- **Recebimentos:** pagamentos com data no período, independentemente da abertura da ordem.
- **Ticket médio:** média do total das ordens entregues, considerando a data do evento de entrega.
- **Tempo médio:** da abertura ao primeiro evento "para Concluído", em dias com uma casa decimal.

As datas são comparadas no horário de Brasília.

### D6. CSV com a biblioteca padrão

`csv.writer` com `delimiter=";"` e `quoting=csv.QUOTE_MINIMAL` (protege `;`, aspas e quebras de linha), BOM `﻿` e valores com vírgula decimal sem o prefixo "R$". O download usa `rx.download(data=..., filename=..., mime_type="text/csv")`, gerado sob demanda no servidor sem gravar arquivos.

### D7. Permissões

`Permission.STAFF_MANAGE` só para Administrador e `Permission.REPORTS_VIEW` para Administrador e Atendente. O menu lateral passa a exibir "Relatórios" e "Colaboradores" conforme as permissões do usuário.

### D8. Xano

As operações `users.list`, `users.create`, `users.update`, `technicians.create` e `technicians.update` entram em `OPERATIONS` sem contrato e falham de forma explícita no adaptador Xano.

## Risks / Trade-offs

- [Contas e alterações em memória no modo demonstração] → mesmo comportamento das demais entidades; documentado.
- [Mudança de cargo durante a sessão] → aplicada na próxima ação do usuário, sem exigir novo login (comportamento desejado).
- [Relatórios calculados percorrendo todas as ordens] → suficiente para o volume de demonstração; com o Xano, os filtros por período poderão ir para o backend quando houver contrato.
