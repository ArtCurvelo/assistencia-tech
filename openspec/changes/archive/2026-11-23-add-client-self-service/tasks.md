# Tasks

## 1. Domínio

- [x] 1.1 Status Solicitado (fluxo, permissão de recebimento, previsão ao receber, sem atraso) e dados de entrega na ordem; testes.
- [x] 1.2 Regras da solicitação e do equipamento pelo portal; permissões do cliente; testes de serviço na demonstração.

## 2. Backend Xano

- [x] 2.1 `os_servicos` (status `solicitado`, `entrega_modo`, `coleta_endereco`, `coleta_periodo`), transições no `PATCH`, `GET/POST /portal/equipamentos` e `POST /portal/solicitacao`; validar, simular e enviar após autorização.
- [x] 2.2 Adaptador, mapeadores e contrato-alvo; testes com servidor simulado.

## 3. Avisos

- [x] 3.1 `Notifier` (Brevo e nulo), mensagens por status, filtros de destinatário e configuração; testes.
- [x] 3.2 Link de WhatsApp no detalhe da ordem.

## 4. Interface

- [x] 4.1 Portal: "Meus equipamentos" e "Solicitar atendimento" com endereço da loja ou dados da coleta.
- [x] 4.2 Equipe: coluna Solicitado no quadro, solicitações em "Precisa de atenção" e entrega no detalhe.

## 5. Verificação

- [x] 5.1 `pytest`, ponta a ponta, `openspec validate --strict`, verificador de contrato e roteiro no Xano real.

## Registro de verificação (2026-11-23)

- **pytest:** 18 testes novos em `tests/test_client_self_service.py`; ponta a ponta: 12 de 12, com o fluxo cliente cadastra equipamento → pede coleta → atendente vê em "Precisa de atenção" e no quadro → confirma o recebimento.
- Na primeira rodada de ponta a ponta, um servidor de teste órfão de outra sessão escutava a mesma porta 8000 e dividia as conexões; encerrado, os testes passaram sem mudança no código.
- **XanoScript:** 67 arquivos válidos; simulação e envio após autorização (67 documentos).
- **Xano real** (cliente de vitrine Larissa Moura, contas de teste):
  - equipamento cadastrado no cliente do token mesmo com `cliente_id` falso na requisição; tipo inválido → 400; lista só com equipamentos dela;
  - outra cliente usando o equipamento → 404; coleta sem endereço → 400;
  - solicitação → 200 `solicitado`, `motoboy`, `Tarde`, sem previsão;
  - técnico tentando receber → 403; pular para Em análise → 400; atendente recebe → `recebido` com previsão hoje + 7 (2026-11-25 no dia do teste);
  - histórico com "Atendimento solicitado pelo cliente (Coleta por motoboy)…"; "em atendimento" nos números públicos: 13 → 13 (solicitado) → 14 (recebido).
- **Dados de teste:** equipamento PlayStation 4 da Larissa e a ordem 27, cancelada no fim do roteiro.
- **Pendente:** envio real de e-mail (depende da chave do serviço de e-mail no ambiente).
