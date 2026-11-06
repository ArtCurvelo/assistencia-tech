# Tasks

## 1. Validadores e valores monetários

- [ ] 1.1 Implementar `domain/validators.py` com normalização, validação e formatação de CPF; verificar com testes cobrindo `529.982.247-25` válido, `123.456.789-00` inválido, `11111111111` inválido e entrada sem pontuação.
- [ ] 1.2 Implementar normalização, validação e formatação de telefone fixo e celular; verificar com testes de `11987654321` → `(11) 98765-4321`, fixo de 10 dígitos, DDD inválido e quantidade errada de dígitos.
- [ ] 1.3 Implementar `parse_brl` e `format_brl` com `Decimal`; verificar com testes de `1.234,56`, `1234.56`, `R$ 1.234,56`, arredondamento em centavos e rejeição de texto inválido.

## 2. Modelos de domínio e dados de demonstração

- [ ] 2.1 Reescrever `models/` com cliente (CPF, telefone), equipamento (`client_id`, tipo, marca, modelo, série, observações), itens de orçamento, pagamentos, eventos de histórico, `OrderStatus` e ordem como agregado; verificar com testes de criação válida e mensagens de validação em português.
- [ ] 2.2 Criar `data/demo/seed.py` com clientes, técnicos, equipamentos e ordens em todos os status, substituindo `services/demo_data.py`; verificar com teste de que todos os dados de demonstração passam pelas validações e regras do domínio.

## 3. Regras da ordem de serviço

- [ ] 3.1 Implementar `domain/order_workflow.py` com a tabela de transições, `allowed_next` e `check_transition` (técnico, diagnóstico, itens, saldo, motivo, status final); verificar com testes para cada transição permitida, cada transição recusada e cada pré-condição.
- [ ] 3.2 Implementar `domain/pricing.py` (totais de serviços e peças, total, pago, saldo, situação Pendente/Parcial/Pago); verificar com o cenário da spec (R$ 120,00 + 2 × R$ 45,50 = R$ 211,00) e com pagamento parcial.
- [ ] 3.3 Implementar `domain/history.py` com a criação de eventos imutáveis; verificar com testes de que cada tipo de evento registra data, hora, autor e descrição.

## 4. Repositórios e serviços de aplicação

- [ ] 4.1 Atualizar os `Protocol`s (get, update, delete, save do agregado, técnicos) e os repositórios de demonstração; verificar com os testes de contrato interno atualizados.
- [ ] 4.2 Implementar `services/clients.py` (cadastro, edição, unicidade de CPF/e-mail, exclusão bloqueada por vínculos, histórico do cliente); verificar com testes de cada cenário da spec `client-management`.
- [ ] 4.3 Implementar `services/equipment.py` (vínculo, unicidade do número de série, bloqueio de troca de cliente e de exclusão com ordens, histórico de manutenção); verificar com testes de cada cenário da spec `equipment-management`.
- [ ] 4.4 Implementar `services/orders.py` (abertura, técnico, diagnóstico, itens, pagamentos, status, cancelamento, histórico e `public_view`); verificar com testes de cada cenário da spec `service-orders`.
- [ ] 4.5 Incluir as novas operações em `data/xano/contracts.py` e no adaptador Xano, mantendo o registro vazio; verificar com o teste de que nenhuma operação envia requisição sem contrato.

## 5. Reestruturação da interface sem mudança de comportamento

- [ ] 5.1 Dividir páginas em `pages/`, componentes em `components/` e estado em subestados, mantendo as rotas atuais; verificar com importação do app, `pytest` e navegação por todas as rotas no navegador.
- [ ] 5.2 Confirmar que nenhum arquivo Python passa de 400 linhas; verificar com contagem de linhas.

## 6. Interface de clientes

- [ ] 6.1 Atualizar o cadastro com CPF e telefone validados e a lista com CPF formatado e pesquisa ampliada; verificar no navegador com CPF válido, inválido e duplicado.
- [ ] 6.2 Adicionar edição em diálogo e exclusão com confirmação e bloqueio por vínculos; verificar no navegador editando um cliente com ordens e tentando excluí-lo.
- [ ] 6.3 Criar `/admin/clientes/[id]` com dados, equipamentos e ordens do cliente; verificar no navegador com cliente existente e com identificador inexistente.

## 7. Interface de equipamentos

- [ ] 7.1 Atualizar o cadastro (marca, modelo, número de série, observações), a lista com filtro por tipo e a pesquisa; verificar no navegador com número de série duplicado e filtro por tipo.
- [ ] 7.2 Adicionar edição, exclusão controlada e histórico de manutenção do equipamento; verificar no navegador com equipamento que possui ordens.

## 8. Interface de ordens de serviço

- [ ] 8.1 Atualizar a abertura de OS com seleção de cliente seguida dos equipamentos desse cliente; verificar no navegador que só os equipamentos do cliente escolhido são oferecidos.
- [ ] 8.2 Atualizar a lista com filtros por status e técnico e colunas de técnico, total e situação do pagamento; verificar no navegador com cada filtro.
- [ ] 8.3 Criar `/admin/ordens/[codigo]` com técnico, diagnóstico, orçamento, valores, pagamentos, seletor de status com apenas os próximos status permitidos, cancelamento com motivo e linha do tempo; verificar no navegador percorrendo uma OS de Recebido até Entregue e uma cancelada.
- [ ] 8.4 Exibir as mensagens de recusa das regras (sem técnico, sem diagnóstico, sem itens, saldo pendente, pagamento acima do saldo); verificar no navegador provocando cada uma.

## 9. Consulta pública e painel

- [ ] 9.1 Atualizar a consulta pública para usar `public_view` (status, equipamento e última atualização, sem dados pessoais); verificar no navegador e com teste do serviço.
- [ ] 9.2 Atualizar os indicadores do painel para os novos status (abertas, aguardando aprovação, prontas para entrega, valor a receber); verificar no navegador conferindo com os dados de demonstração.

## 10. Documentação e verificação integrada

- [ ] 10.1 Criar `docs/DATA_MODEL.md` com o diagrama entidade-relacionamento (Mermaid) e o diagrama de estados da OS, e atualizar `docs/REQUIREMENTS.md` com os novos requisitos funcionais; verificar conferindo cada requisito com as specs.
- [ ] 10.2 Executar `pytest`, `openspec validate expand-service-domain --strict` e a contagem de linhas, e registrar os resultados neste arquivo.
- [ ] 10.3 Percorrer no navegador o roteiro completo (cliente → equipamento → OS de Recebido a Entregue → consulta pública) nos modos demonstração e Xano sem contratos, e registrar os resultados neste arquivo.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
