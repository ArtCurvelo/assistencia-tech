# Tasks

## 1. Domínio

- [ ] 1.1 Status Solicitado (fluxo, permissão de recebimento, previsão ao receber, sem atraso) e dados de entrega na ordem; testes.
- [ ] 1.2 Regras da solicitação e do equipamento pelo portal; permissões do cliente; testes de serviço na demonstração.

## 2. Backend Xano

- [ ] 2.1 `os_servicos` (status `solicitado`, `entrega_modo`, `coleta_endereco`, `coleta_periodo`), transições no `PATCH`, `GET/POST /portal/equipamentos` e `POST /portal/solicitacao`; validar, simular e enviar após autorização.
- [ ] 2.2 Adaptador, mapeadores e contrato-alvo; testes com servidor simulado.

## 3. Avisos

- [ ] 3.1 `Notifier` (Brevo e nulo), mensagens por status, filtros de destinatário e configuração; testes.
- [ ] 3.2 Link de WhatsApp no detalhe da ordem.

## 4. Interface

- [ ] 4.1 Portal: "Meus equipamentos" e "Solicitar atendimento" com endereço da loja ou dados da coleta.
- [ ] 4.2 Equipe: coluna Solicitado no quadro, solicitações em "Precisa de atenção" e entrega no detalhe.

## 5. Verificação

- [ ] 5.1 `pytest`, ponta a ponta, `openspec validate --strict`, verificador de contrato e roteiro no Xano real.
