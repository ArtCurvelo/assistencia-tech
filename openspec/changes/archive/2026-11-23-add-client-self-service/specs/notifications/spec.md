# Spec Delta

## ADDED Requirements

### Requirement: Aviso por e-mail ao cliente

Quando o envio de e-mail estiver configurado, o sistema SHALL enviar ao e-mail do cliente um aviso na abertura da ordem e a cada mudança de status, com o código da ordem, o novo status, o que acontece em seguida e o link da consulta pública. O aviso MUST NOT conter valores, diagnóstico ou dados pessoais além do primeiro nome.

#### Scenario: Orçamento pronto
- **WHEN** o técnico move a ordem para Aguardando aprovação
- **THEN** o cliente recebe um e-mail avisando que o orçamento está disponível no portal

### Requirement: Envio de avisos sem prejudicar a operação

Uma falha no envio MUST NOT desfazer nem impedir a operação que gerou o aviso. Sem configuração de e-mail, no modo demonstração, para cadastros anonimizados e para endereços de domínios reservados a testes, nenhum e-mail SHALL ser enviado.

#### Scenario: Serviço de e-mail fora do ar
- **WHEN** o envio falha ao mover a ordem para Concluído
- **THEN** a ordem fica Concluída e a falha é registrada no log

#### Scenario: Cliente de teste
- **WHEN** o e-mail do cliente termina em `@exemplo.test`
- **THEN** nenhum e-mail é enviado

### Requirement: Aviso pelo WhatsApp

O detalhe da ordem SHALL oferecer à equipe o botão "Avisar pelo WhatsApp", que abre uma conversa com o telefone do cliente e a mensagem do status atual já escrita. O botão MUST NOT aparecer quando o cliente não tem telefone válido.

#### Scenario: Ordem pronta para retirada
- **WHEN** a atendente aciona o botão numa ordem Concluída
- **THEN** o WhatsApp abre com o número do cliente e a mensagem de que o equipamento está pronto
