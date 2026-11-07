# Proposal: Aprovação do orçamento pelo cliente

## Why

Hoje o orçamento enviado em "Aguardando aprovação" é aprovado ou cancelado por um colaborador, que registra a decisão do cliente informada por telefone ou no balcão. O cliente vê o orçamento no portal, mas não pode respondê-lo. Isso deixa o ciclo do atendimento incompleto, depende de um contato manual e não registra quem decidiu. Permitir que o próprio cliente aprove ou recuse o orçamento no portal fecha o ciclo, reduz o tempo parado em "Aguardando aprovação" e deixa a decisão registrada no histórico com autoria.

## What Changes

- No detalhe de uma ordem própria em "Aguardando aprovação", o portal oferece **Aprovar orçamento** e **Recusar orçamento**, mostrando o total.
- **Aprovar** move a ordem para "Em reparo". **Recusar** exige um motivo e move a ordem para "Cancelado", com o motivo registrado no cancelamento.
- Cada decisão registra no histórico um evento "Decisão do cliente", com o cliente como autor, além da mudança de status. O andamento do portal passa a mostrar essa decisão.
- A decisão só vale para ordens do próprio cliente e somente em "Aguardando aprovação"; as regras são aplicadas na aplicação e repetidas no backend.
- A aprovação por colaborador continua disponível (decisão informada por telefone).
- Backend Xano: novo endpoint `POST /portal/decisao_orcamento` (perfil cliente), que grava a decisão, o status e o histórico numa transação.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `customer-portal`: novo requisito de decisão do orçamento pelo cliente.
- `access-control`: o perfil Cliente ganha a permissão de decidir o orçamento das próprias ordens.

## Impact

- **Código:** `domain` (operação e evento da decisão, permissão), `services/portal.py`, `data/repositories.py` (`PortalRepository`), modo demonstração, adaptador Xano, `state/portal.py`, `pages/portal.py`, `presenters.py`.
- **Backend:** `xano/api/atech_os/portal/decisao_orcamento_post.xs`; contrato-alvo com 29 endpoints.
- **Testes:** domínio, serviço (demonstração e Xano simulado) e verificador de contrato.

## Out of Scope

- Cobrança de taxa de diagnóstico na recusa.
- Notificação do cliente por e-mail ou mensagem.
- Aprovação parcial (somente alguns itens).
