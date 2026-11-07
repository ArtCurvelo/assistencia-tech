# Spec Delta

## MODIFIED Requirements

### Requirement: Matriz de permissões

As permissões SHALL ser concedidas por perfil conforme a matriz: Administrador tem todas as permissões administrativas; Atendente vê painel, clientes, equipamentos, ordens e estoque, cadastra e edita clientes, equipamentos e peças, registra entradas de estoque, abre ordens, atribui técnico, registra aprovação, pagamentos, entrega e cancelamento; Técnico vê painel, clientes, equipamentos, ordens e estoque, e registra diagnóstico, orçamento e status técnicos; Cliente acessa apenas o portal. Somente o Administrador exclui clientes e equipamentos.

#### Scenario: Atendente tenta excluir cliente
- **WHEN** um atendente tenta excluir um cliente
- **THEN** a operação é recusada com a mensagem de que o perfil não tem permissão para essa ação

#### Scenario: Técnico tenta registrar pagamento
- **WHEN** um técnico tenta registrar um pagamento
- **THEN** a operação é recusada por falta de permissão

#### Scenario: Técnico tenta repor estoque
- **WHEN** um técnico tenta registrar uma entrada de estoque
- **THEN** a operação é recusada por falta de permissão, mas o técnico continua consultando o estoque
