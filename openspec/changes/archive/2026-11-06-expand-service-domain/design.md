# Design: Domínio completo de clientes, equipamentos e ordens de serviço

## Context

Motivação em `proposal.md`; comportamento em `specs/client-management`, `specs/equipment-management` e `specs/service-orders`.

Estado atual (após os grupos 1–5 de `integrate-xano-backend`, commit `eb99428`):

- `models/entities.py` tem modelos Pydantic congelados com vínculos por **nome** (`Equipment.client`, `ServiceOrder.client` e `device` em texto livre).
- `data/repositories.py` define `Protocol`s com `list`/`create` e, para ordens, `get_by_code`/`update_status`. As regras de negócio (cliente existente, e-mail único, código da OS) estão dentro dos repositórios de demonstração.
- `state.py` (231 linhas) é um único `AppState`; `assistencia_tech.py` (357 linhas) contém todas as páginas; `components.py` contém layout e feedback.
- Reflex 0.8.28 oferece `router.page.params` para rotas dinâmicas, `rx.dialog`/`rx.alert_dialog` e `rx.toast`.

## Goals / Non-Goals

**Goals:**

- As regras de negócio ficam em funções puras e testáveis, independentes da fonte de dados, e valem igualmente para o modo demonstração e o Xano.
- Repositórios cuidam apenas de persistência; a orquestração fica em serviços de aplicação.
- Nenhum arquivo Python passa de 400 linhas após a reestruturação.

**Non-Goals:**

- Visual final das novas telas (a mudança de frontend fará o refinamento); aqui a meta é ficarem funcionais, consistentes com o sistema visual atual e acessíveis.
- Concorrência entre usuários simultâneos editando a mesma ordem.

## Decisions

### D1. Camadas: domínio puro → serviços de aplicação → repositórios

```
assistencia_tech/
  domain/                 # regras puras, sem I/O
    validators.py         # CPF, telefone, dinheiro (parse/format)
    order_workflow.py     # status, transições e pré-condições
    pricing.py            # totais, saldo, situação do pagamento
    history.py            # criação de eventos do histórico
  models/                 # entidades e objetos de valor (Pydantic)
  services/               # serviços de aplicação (orquestração)
    clients.py  equipment.py  orders.py
  data/                   # repositórios (persistência) — demo e Xano
    demo/seed.py          # dados de demonstração (substitui services/demo_data.py)
```

Os serviços recebem o `DataGateway` e um relógio, validam a entrada, aplicam as regras do domínio, gravam pelo repositório e registram o histórico. As regras que hoje estão no repositório de demonstração (cliente existente, e-mail único) migram para os serviços.

- *Alternativa:* manter as regras nos repositórios. Rejeitada: o adaptador Xano teria de duplicá-las.
- *Alternativa:* confiar ao backend todas as regras. Rejeitada: os contratos do Xano são desconhecidos, e as regras precisam ser demonstráveis e testáveis agora. Se o Xano também validar, as duas camadas convivem; as mensagens do backend são traduzidas pela hierarquia de erros existente.

### D2. Ordem de serviço como agregado

`ServiceOrder` contém seus `items` (serviços e peças), `payments` e `history`. O repositório oferece `get_by_code` e `save(order)`, gravando o agregado inteiro. Itens, pagamentos e eventos não têm repositório próprio.

- *Alternativa:* repositórios separados para itens e pagamentos. Rejeitada: mais operações no contrato e risco de estados inconsistentes; o agregado garante que as regras sejam avaliadas sobre a ordem completa.

### D3. Vínculos por identificador e leitura enriquecida

Equipamentos guardam `client_id`; ordens guardam `client_id` e `equipment_id`. A interface recebe dados já "montados" (nome do cliente, descrição do equipamento) gerados pelos serviços, de modo que renomear um cliente se reflete em todas as listas sem cópias de nome.

### D4. Status e transições como dados

`OrderStatus` é um `StrEnum`. As transições ficam em uma tabela `TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]]` e as pré-condições (técnico, diagnóstico, itens, saldo, motivo) em funções que retornam a mensagem de recusa. `allowed_next(order)` alimenta o seletor da interface; `check_transition(order, target, reason)` é chamado pelo serviço antes de gravar.

### D5. Dinheiro com `Decimal`

Valores são `Decimal` com quantização em centavos (`ROUND_HALF_UP`). `parse_brl` aceita `1234.56`, `1.234,56` e `R$ 1.234,56`; `format_brl` produz `R$ 1.234,56`. `float` nunca é usado em valores.

### D6. Documentos e contatos normalizados

CPF e telefone são armazenados só com dígitos e formatados na exibição. A validação do CPF usa os dois dígitos verificadores e rejeita sequências repetidas. O telefone aceita 10 dígitos (fixo) ou 11 dígitos com `9` após o DDD; o DDD deve estar entre 11 e 99.

### D7. Tempo e autoria injetáveis

Os serviços recebem um `Clock` (padrão: horário de Brasília via `zoneinfo`) e um `actor` (padrão: "Usuário demonstração"). Os testes usam relógio fixo; a mudança de autenticação substituirá o `actor` pelo usuário logado.

### D8. Reestruturação da interface

- `pages/` com um módulo por área (`public.py`, `dashboard.py`, `clients.py`, `equipment.py`, `orders.py`, `order_detail.py`); `assistencia_tech.py` apenas registra rotas.
- `components/` dividido em `layout.py`, `feedback.py`, `forms.py` e `dialogs.py`.
- Estado em subestados Reflex: `AppState` (fonte de dados, feedback, carregamento) e `ClientState`, `EquipmentState`, `OrderState`, `OrderDetailState` e `TrackingState` herdando dele.
- Rotas dinâmicas `/admin/clientes/[id]` e `/admin/ordens/[codigo]`, lidas por `self.router.page.params` no `on_load`.
- Confirmações com `rx.alert_dialog`; edições com `rx.dialog` contendo formulário.

### D9. Consulta pública por projeção

O serviço de ordens expõe `public_view(code)`, que retorna um objeto `PublicOrderView` contendo apenas código, status, equipamento e data da última atualização. A página pública só tem acesso a essa projeção, o que impede o vazamento de dados por construção.

### D10. Contratos Xano

`OPERATIONS` em `data/xano/contracts.py` recebe as novas operações internas (`clients.get`, `clients.update`, `clients.delete`, `equipment.get`, `equipment.update`, `equipment.delete`, `orders.save`, `technicians.list`). O registro continua vazio, e o teste que garante nenhuma requisição sem contrato passa a cobrir todas elas.

### D11. Dados de demonstração

O `seed.py` passa a conter 6 clientes com CPFs fictícios gerados e válidos pelo algoritmo, 3 técnicos, 8 equipamentos e ordens em todos os status, com itens, pagamentos e histórico coerentes com as regras. Isso permite demonstrar cada regra sem preparação manual.

## Risks / Trade-offs

- [CPFs válidos gerados podem coincidir com CPFs reais] → são usados apenas nos dados fictícios, identificados como demonstração, e sem nenhum outro dado pessoal real associado.
- [Mudança grande, com risco de regressões] → grupos de tarefas com testes próprios, e a reestruturação da interface feita sem mudança de comportamento e validada antes das novas telas.
- [Gravar o agregado inteiro pode não corresponder aos endpoints do Xano] → o adaptador Xano poderá decompor `save` em várias chamadas quando os contratos forem conhecidos; a interface interna não muda.
- [Dados de demonstração compartilhados por processo] → mantido da mudança anterior e documentado.

## Migration Plan

1. Domínio, modelos e serviços entram com testes, sem tocar a interface.
2. A interface é reestruturada em módulos, preservando o comportamento (verificação no navegador).
3. As telas novas são ligadas aos serviços, área por área.
4. Rollback: cada grupo vira um commit próprio e pode ser revertido isoladamente.
