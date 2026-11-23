# Proposal: Autoatendimento do cliente e avisos

## Why

Hoje o cliente só acompanha: para ser atendido, precisa ir à assistência, e a atendente cadastra o equipamento e abre a ordem. O cliente também só fica sabendo do andamento se entrar no portal. Uma assistência atual deixa o cliente iniciar o atendimento pela internet, escolher como o equipamento chega e ser avisado a cada etapa.

## What Changes

- **Meus equipamentos:** o cliente cadastra e vê os próprios equipamentos no portal.
- **Solicitar atendimento:** o cliente escolhe um equipamento, descreve o problema e a forma de entrega:
  - **Levar à loja:** o portal mostra o endereço e o horário da assistência (configuráveis);
  - **Coleta por motoboy:** o cliente informa o endereço de coleta e o período de preferência; sem taxa.
- **Novo status "Solicitado":** a ordem pedida pelo cliente começa em Solicitado, porque o equipamento ainda não chegou. A atendente confirma o recebimento (Solicitado → Recebido), e a previsão de entrega passa a contar daí. A solicitação pode ser cancelada.
- **Avisos ao cliente:** na abertura da ordem e a cada mudança de status, o sistema envia um e-mail ao cliente (serviço Brevo, quando configurado). No detalhe da ordem, a equipe tem o botão "Avisar pelo WhatsApp", que abre a conversa com a mensagem pronta.
- **Equipe:** as solicitações aparecem em "Precisa de atenção", numa coluna do quadro e com os dados da entrega no detalhe.
- **Xano:** status `solicitado`, campos de entrega em `os_servicos` e endpoints `GET/POST /portal/equipamentos` e `POST /portal/solicitacao`.

## Capabilities

### New Capabilities

- `notifications`: avisos ao cliente por e-mail e link de WhatsApp.

### Modified Capabilities

- `customer-portal`: equipamentos e solicitação de atendimento.
- `service-orders`: status Solicitado e dados de entrega.

## Impact

- **Backend:** tabela `os_servicos` (enum e 3 campos), `PATCH /os_servicos/{id}` (transições de Solicitado) e 3 endpoints novos do portal.
- **Código:** modelos, fluxo de status, permissões, repositórios (demonstração e Xano), `PortalService`, serviço de avisos, configuração, portal, detalhe da ordem, painel e quadro.
- **Configuração:** `ASSISTENCIA_STORE_ADDRESS`, `ASSISTENCIA_STORE_HOURS`, `BREVO_API_KEY` e `ASSISTENCIA_EMAIL_FROM` (no Render, nunca no repositório).
- **Testes:** domínio, serviço, adaptador simulado, avisos e ponta a ponta.

## Out of Scope

- SMS e WhatsApp automáticos (serviços pagos).
- Taxa, rastreio ou agendamento com hora marcada do motoboy.
- Cancelamento da solicitação pelo próprio cliente.
