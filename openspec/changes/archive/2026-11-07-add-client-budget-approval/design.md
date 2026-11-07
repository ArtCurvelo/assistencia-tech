# Design: Aprovação do orçamento pelo cliente

## Context

O fluxo de status é `Recebido → Em análise → Aguardando aprovação → Em reparo → Concluído → Entregue`, com cancelamento possível até o reparo. A transição "Aguardando aprovação → Em reparo" exige a permissão `orders.approve` (Administrador e Atendente). O portal (`PortalService`) só lê dados, e no Xano o perfil cliente acessa apenas os endpoints `portal/*`, que filtram pelo token.

## Decisions

### D1. Operação de domínio própria

`order_operations.client_decision(order, approve, reason, at, author)` valida que a ordem está em "Aguardando aprovação", exige o motivo na recusa e aplica `change_status` (para "Em reparo" ou "Cancelado"), acrescentando antes um evento `Decisão do cliente`. Reaproveitar `change_status` mantém as pré-condições do fluxo num só lugar.

### D2. Permissão separada

Nova permissão `portal.decide_budget`, somente do perfil Cliente. Não reaproveita `orders.approve` porque o cliente não aprova ordens de terceiros nem recusa por outro caminho além do portal.

### D3. Persistência pela interface do portal

`PortalRepository.save_client_decision(client_id, order, approve, reason)` recebe a ordem já atualizada pelo domínio. O modo demonstração grava o agregado; o Xano chama `POST /portal/decisao_orcamento`, que repete as validações e grava status e histórico numa transação. O texto dos eventos é o mesmo nos dois lados ("Orçamento aprovado pelo cliente." / "Orçamento recusado pelo cliente. Motivo: …").

### D4. Recusa cancela a ordem

Recusar move para "Cancelado" com o motivo "Orçamento recusado pelo cliente: …". A ordem cancelada continua podendo ser marcada como "Entregue" quando o equipamento é devolvido, sem exigir quitação, como já acontece hoje.

## Risks / Trade-offs

- [Decisão por engano] → a recusa pede confirmação com motivo; a aprovação é reversível pelo colaborador apenas por cancelamento, o que fica no histórico.
- [Corrida entre colaborador e cliente] → o backend confere o status atual antes de gravar; quem chegar depois recebe "Esta ordem não está aguardando a sua aprovação."
