# customer-portal Specification

## Purpose
Define a área do cliente no Assistência TECH, onde o cliente autenticado acompanha as próprias ordens de serviço, sem acesso a dados de outros clientes ou a funções administrativas.

## Requirements

### Requirement: Lista das próprias ordens

O portal (`/minha-conta`) SHALL exigir sessão de um usuário Cliente e SHALL listar somente as ordens do cliente associado à conta, da mais recente para a mais antiga, com código, equipamento, status, data da última atualização, total e saldo.

#### Scenario: Cliente com ordens
- **WHEN** um cliente com duas ordens abre o portal
- **THEN** as duas ordens são exibidas e nenhuma ordem de outro cliente aparece

#### Scenario: Cliente sem ordens
- **WHEN** um cliente sem ordens abre o portal
- **THEN** o portal informa que não há ordens de serviço e indica como solicitar atendimento

#### Scenario: Colaborador no portal
- **WHEN** um colaborador abre `/minha-conta`
- **THEN** ele é levado ao painel administrativo

### Requirement: Detalhe da própria ordem

O portal SHALL exibir o detalhe de uma ordem do próprio cliente com status, equipamento, problema relatado, diagnóstico, itens do orçamento, valores, pagamentos e o andamento dos status, sem dados internos como autores e técnicos.

#### Scenario: Ordem própria
- **WHEN** o cliente abre o detalhe de uma de suas ordens
- **THEN** são exibidos o orçamento, os valores e as mudanças de status com data

#### Scenario: Ordem de outro cliente
- **WHEN** o cliente tenta abrir o detalhe de uma ordem de outro cliente pelo endereço
- **THEN** a página informa que a ordem não foi encontrada, sem revelar se ela existe

### Requirement: Dados da conta

O portal SHALL exibir o nome, o e-mail, o CPF mascarado (apenas os dois últimos dígitos visíveis) e o telefone do cliente.

#### Scenario: CPF mascarado
- **WHEN** o cliente com CPF `529.982.247-25` abre o portal
- **THEN** o CPF é exibido como `***.***.***-25`
