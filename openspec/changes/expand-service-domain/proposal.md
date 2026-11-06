# Proposal: Domínio completo de clientes, equipamentos e ordens de serviço

## Why

O modelo atual cobre apenas o cadastro mínimo: clientes com nome, e-mail e telefone; equipamentos e ordens vinculados ao cliente **pelo nome**; e ordens com quatro status livres, sem diagnóstico, valores ou histórico. Isso não representa o funcionamento real de uma assistência técnica nem permite demonstrar regras de negócio na avaliação. Com a camada de dados pronta (mudança `integrate-xano-backend`), é o momento de modelar o domínio completo atrás das mesmas interfaces, para que a futura integração com o Xano receba um modelo já consolidado.

## What Changes

- **Clientes:** CPF validado pelos dígitos verificadores e único, telefone brasileiro validado, edição de dados, exclusão controlada (confirmação e bloqueio quando houver equipamentos ou ordens) e página de detalhe com o histórico de atendimentos.
- **Equipamentos:** vínculo com o cliente por identificador, marca, modelo, número de série opcional e único, observações (acessórios, estado de entrega), edição, exclusão controlada e histórico de manutenções.
- **Ordens de serviço:** vínculo obrigatório com cliente e com um equipamento desse cliente, técnico responsável, diagnóstico técnico, orçamento com serviços e peças, valores calculados, pagamentos e histórico de alterações.
- **BREAKING (interno):** o conjunto de status passa a ser `Recebido`, `Em análise`, `Aguardando aprovação`, `Em reparo`, `Concluído`, `Entregue` e `Cancelado`, com transições permitidas definidas. A mudança `integrate-xano-backend` tem seu cenário de status inválido ajustado para referenciar o conjunto permitido em vez de listá-lo.
- **BREAKING (interno):** equipamentos e ordens deixam de guardar o nome do cliente e passam a referenciar identificadores. Os dados de demonstração são migrados para o novo modelo.
- **Interface:** página de detalhe da OS (`/admin/ordens/[codigo]`) com linha do tempo, página de detalhe do cliente (`/admin/clientes/[id]`), formulários de edição e diálogos de confirmação. O refinamento visual amplo fica para a mudança de frontend.
- **Consulta pública de OS:** passa a exibir o status e a data da última atualização, sem dados pessoais do cliente.

## Capabilities

### New Capabilities

- `client-management`: cadastro, validação, edição, exclusão controlada e histórico de clientes.
- `equipment-management`: cadastro, vínculo com cliente, edição, exclusão controlada e histórico de manutenção de equipamentos.
- `service-orders`: ciclo de vida da ordem de serviço — abertura, status e transições, técnico responsável, diagnóstico, orçamento, pagamentos, histórico e consulta pública.

### Modified Capabilities

- Nenhuma especificação vigente em `openspec/specs/` tem requisitos alterados. O ajuste do conjunto de status é feito no delta `data-source` da mudança ainda não arquivada `integrate-xano-backend`.

## Impact

- **Código:** `models/` (novas entidades e valores), `data/repositories.py` (novas operações), `data/demo/` (regras de negócio e dados migrados), `data/xano/contracts.py` (novas operações internas, todas sem contrato), `state.py` (dividido por domínio), páginas e componentes administrativos.
- **Dados de demonstração:** `services/demo_data.py` reescrito com identificadores, CPFs válidos fictícios, técnicos e ordens em diferentes etapas.
- **Testes:** validadores (CPF, telefone, valores), regras de transição de status, cálculos financeiros, exclusão controlada e histórico.

## Assumptions

Decisões tomadas por padrão, registradas para revisão antes da implementação:

- Técnicos responsáveis vêm de uma lista simples (nome e especialidade) nos dados de demonstração; o gerenciamento de colaboradores, cargos e permissões é de outra mudança.
- Enquanto não houver autenticação, o autor registrado no histórico é "Usuário demonstração".
- Pagamentos aceitam Dinheiro, PIX, Cartão de débito e Cartão de crédito; não há parcelamento nem integração com meios de pagamento.
- Valores em reais com duas casas decimais; não há desconto nem impostos nesta mudança.
- A exclusão é bloqueada quando há vínculos, em vez de inativação lógica.

## Out of Scope

- Autenticação, perfis e permissões por cargo.
- Gerenciamento de colaboradores e relatórios operacionais.
- Estoque de peças (as peças são registradas por OS, sem controle de estoque).
- Emissão de nota fiscal, recibo em PDF ou envio de notificações ao cliente.
- Contratos reais do Xano para as novas operações (seguem a regra de contratos documentados).
