# Proposal: Prazos e garantia

## Why

A ordem de serviço não tem prazo: não há como dizer ao cliente quando o equipamento fica pronto, nem como a equipe saber quais ordens estão atrasadas. Depois da entrega, também não existe garantia: se o mesmo defeito voltar, a nova ordem é aberta como se fosse um atendimento comum, cobrada de novo e sem ligação com o reparo anterior. O Código de Defesa do Consumidor (art. 26, II) dá 90 dias para reclamar de vícios em serviços e produtos duráveis; a assistência precisa controlar esse prazo e atender a garantia sem cobrança, com rastreabilidade.

## What Changes

- **Previsão de entrega** em toda ordem: informada na abertura (padrão de 7 dias) e alterável por Administrador e Atendente enquanto a ordem não estiver Entregue ou Cancelada; cada alteração vai para o histórico.
- **Ordens atrasadas:** antes de Concluído, uma ordem com previsão vencida aparece como "Atrasada" (com os dias de atraso) na lista, no detalhe e num alerta do painel.
- **Garantia de 90 dias** a partir da entrega de uma ordem concluída (entregas de ordens canceladas não têm garantia). O detalhe, o portal e a consulta da equipe mostram "Garantia até".
- **Ordem em garantia:** dentro do prazo, Administrador e Atendente abrem, a partir da ordem original, uma nova ordem ligada a ela, para o mesmo cliente e equipamento. Ordens em garantia não geram cobrança: o orçamento registra serviços e peças, mas o total a pagar é zero.
- Portal e consulta pública mostram a previsão de entrega; o portal mostra também a garantia.
- Backend Xano: campos `previsao_entrega` e `garantia_de` em `os_servicos`, com as regras de garantia conferidas no servidor.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `service-orders`: previsão de entrega, ordens atrasadas, garantia, ordem em garantia e consulta pública com previsão.
- `customer-portal`: previsão de entrega e garantia no portal.

## Impact

- **Código:** `models` (previsão e vínculo de garantia), `domain/deadlines.py`, `domain/pricing.py` (ordem em garantia sem cobrança), `services/orders.py`, adaptadores (demonstração e Xano), presenters, páginas de ordens, detalhe, painel, portal e consulta pública.
- **Backend:** `os_servicos` (POST, PATCH, GET, `consulta_publica`, `portal/minhas_ordens`).
- **Testes:** domínio, serviço e adaptador Xano simulado.

## Out of Scope

- Prazo em dias úteis e feriados.
- Garantia com prazo diferente por tipo de serviço ou peça.
- Notificação automática de atraso ao cliente.
