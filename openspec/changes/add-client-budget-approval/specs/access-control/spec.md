# Spec Delta

## MODIFIED Requirements

### Requirement: Permissões por mudança de status

As mudanças de status SHALL exigir permissões específicas: iniciar análise, enviar para aprovação e concluir o reparo são ações técnicas (Administrador e Técnico); registrar a aprovação do orçamento (Aguardando aprovação → Em reparo), entregar e cancelar são ações de atendimento (Administrador e Atendente). O Cliente SHALL poder aprovar ou recusar, pelo portal, somente o orçamento das próprias ordens em "Aguardando aprovação"; nenhuma outra mudança de status é permitida ao Cliente.

#### Scenario: Atendente registra aprovação
- **WHEN** um atendente move uma ordem de Aguardando aprovação para Em reparo
- **THEN** o status é alterado e o histórico registra o atendente como autor

#### Scenario: Técnico tenta entregar
- **WHEN** um técnico tenta mover uma ordem Concluída para Entregue
- **THEN** a alteração é recusada por falta de permissão

#### Scenario: Cliente decide o próprio orçamento
- **WHEN** um cliente aprova pelo portal o orçamento de uma ordem própria em Aguardando aprovação
- **THEN** o status é alterado para Em reparo e o histórico registra o cliente como autor

#### Scenario: Colaborador tenta usar a decisão do cliente
- **WHEN** um colaborador tenta registrar uma decisão pelo recurso do portal
- **THEN** a operação é recusada por falta de permissão
