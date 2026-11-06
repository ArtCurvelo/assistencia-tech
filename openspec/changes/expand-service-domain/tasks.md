# Tasks

## 1. Validadores e valores monetários

- [x] 1.1 Implementar `domain/validators.py` com normalização, validação e formatação de CPF; verificar com testes cobrindo `529.982.247-25` válido, `123.456.789-00` inválido, `11111111111` inválido e entrada sem pontuação.
- [x] 1.2 Implementar normalização, validação e formatação de telefone fixo e celular; verificar com testes de `11987654321` → `(11) 98765-4321`, fixo de 10 dígitos, DDD inválido e quantidade errada de dígitos.
- [x] 1.3 Implementar `parse_brl` e `format_brl` com `Decimal`; verificar com testes de `1.234,56`, `1234.56`, `R$ 1.234,56`, arredondamento em centavos e rejeição de texto inválido.

## 2. Modelos de domínio e dados de demonstração

- [x] 2.1 Reescrever `models/` com cliente (CPF, telefone), equipamento (`client_id`, tipo, marca, modelo, série, observações), itens de orçamento, pagamentos, eventos de histórico, `OrderStatus` e ordem como agregado; verificar com testes de criação válida e mensagens de validação em português.
- [x] 2.2 Criar `data/demo/seed.py` com clientes, técnicos, equipamentos e ordens em todos os status, substituindo `services/demo_data.py`; verificar com teste de que todos os dados de demonstração passam pelas validações e regras do domínio.

## 3. Regras da ordem de serviço

- [x] 3.1 Implementar `domain/order_workflow.py` com a tabela de transições, `allowed_next` e `check_transition` (técnico, diagnóstico, itens, saldo, motivo, status final); verificar com testes para cada transição permitida, cada transição recusada e cada pré-condição.
- [x] 3.2 Implementar `domain/pricing.py` (totais de serviços e peças, total, pago, saldo, situação Pendente/Parcial/Pago); verificar com o cenário da spec (R$ 120,00 + 2 × R$ 45,50 = R$ 211,00) e com pagamento parcial.
- [x] 3.3 Implementar `domain/history.py` com a criação de eventos imutáveis; verificar com testes de que cada tipo de evento registra data, hora, autor e descrição.

## 4. Repositórios e serviços de aplicação

- [x] 4.1 Atualizar os `Protocol`s (get, update, delete, save do agregado, técnicos) e os repositórios de demonstração; verificar com os testes de contrato interno atualizados.
- [x] 4.2 Implementar `services/clients.py` (cadastro, edição, unicidade de CPF/e-mail, exclusão bloqueada por vínculos, histórico do cliente); verificar com testes de cada cenário da spec `client-management`.
- [x] 4.3 Implementar `services/equipment.py` (vínculo, unicidade do número de série, bloqueio de troca de cliente e de exclusão com ordens, histórico de manutenção); verificar com testes de cada cenário da spec `equipment-management`.
- [x] 4.4 Implementar `services/orders.py` (abertura, técnico, diagnóstico, itens, pagamentos, status, cancelamento, histórico e `public_view`); verificar com testes de cada cenário da spec `service-orders`.
- [x] 4.5 Incluir as novas operações em `data/xano/contracts.py` e no adaptador Xano, mantendo o registro vazio; verificar com o teste de que nenhuma operação envia requisição sem contrato.

## 5. Reestruturação da interface sem mudança de comportamento

- [x] 5.1 Dividir páginas em `pages/`, componentes em `components/` e estado em subestados, mantendo as rotas atuais; verificar com importação do app, `pytest` e navegação por todas as rotas no navegador.
- [x] 5.2 Confirmar que nenhum arquivo Python passa de 400 linhas; verificar com contagem de linhas.

## 6. Interface de clientes

- [x] 6.1 Atualizar o cadastro com CPF e telefone validados e a lista com CPF formatado e pesquisa ampliada; verificar no navegador com CPF válido, inválido e duplicado.
- [x] 6.2 Adicionar edição em diálogo e exclusão com confirmação e bloqueio por vínculos; verificar no navegador editando um cliente com ordens e tentando excluí-lo.
- [x] 6.3 Criar `/admin/clientes/[id]` com dados, equipamentos e ordens do cliente; verificar no navegador com cliente existente e com identificador inexistente.

## 7. Interface de equipamentos

- [x] 7.1 Atualizar o cadastro (marca, modelo, número de série, observações), a lista com filtro por tipo e a pesquisa; verificar no navegador com número de série duplicado e filtro por tipo.
- [x] 7.2 Adicionar edição, exclusão controlada e histórico de manutenção do equipamento; verificar no navegador com equipamento que possui ordens.

## 8. Interface de ordens de serviço

- [x] 8.1 Atualizar a abertura de OS com seleção de cliente seguida dos equipamentos desse cliente; verificar no navegador que só os equipamentos do cliente escolhido são oferecidos.
- [x] 8.2 Atualizar a lista com filtros por status e técnico e colunas de técnico, total e situação do pagamento; verificar no navegador com cada filtro.
- [x] 8.3 Criar `/admin/ordens/[codigo]` com técnico, diagnóstico, orçamento, valores, pagamentos, seletor de status com apenas os próximos status permitidos, cancelamento com motivo e linha do tempo; verificar no navegador percorrendo uma OS de Recebido até Entregue e uma cancelada.
- [x] 8.4 Exibir as mensagens de recusa das regras (sem técnico, sem diagnóstico, sem itens, saldo pendente, pagamento acima do saldo); verificar no navegador provocando cada uma.

## 9. Consulta pública e painel

- [x] 9.1 Atualizar a consulta pública para usar `public_view` (status, equipamento e última atualização, sem dados pessoais); verificar no navegador e com teste do serviço.
- [x] 9.2 Atualizar os indicadores do painel para os novos status (abertas, aguardando aprovação, prontas para entrega, valor a receber); verificar no navegador conferindo com os dados de demonstração.

## 10. Documentação e verificação integrada

- [x] 10.1 Criar `docs/DATA_MODEL.md` com o diagrama entidade-relacionamento (Mermaid) e o diagrama de estados da OS, e atualizar `docs/REQUIREMENTS.md` com os novos requisitos funcionais; verificar conferindo cada requisito com as specs.
- [x] 10.2 Executar `pytest`, `openspec validate expand-service-domain --strict` e a contagem de linhas, e registrar os resultados neste arquivo.
- [x] 10.3 Percorrer no navegador o roteiro completo (cliente → equipamento → OS de Recebido a Entregue → consulta pública) nos modos demonstração e Xano sem contratos, e registrar os resultados neste arquivo.

## Registro de verificação (2026-11-06)

**Testes automatizados (`.venv`, `python -m pytest`):** 146 aprovados, 0 falhas.
`test_validators` (CPF, telefone, reais), `test_models`, `test_order_rules` (transições, pré-condições, valores, orçamento, histórico), `test_services` (cenários das três specs), `test_presenters`, `test_demo_gateway` (inclui consistência do seed), `test_xano` (16 operações sem contrato, nenhuma requisição enviada), `test_config`, `test_factory`.

**Tamanho dos arquivos:** maior arquivo Python com 254 linhas (`pages/order_detail.py`); meta de 400 respeitada.

**Navegador — modo demonstração:**
- Painel: 5 em aberto, 1 aguardando aprovação, 1 pronta, R$ 706,00 a receber (conferido com o seed), distribuição por status e ordens recentes.
- Clientes: CPF inválido, telefone inválido e CPF duplicado recusados com mensagem; cadastro válido exibido como `529.982.247-25` / `(11) 98765-4321`; busca por `52998224725`; edição em diálogo pré-preenchida, com recusa de e-mail de outro cliente e alteração do nome; exclusão de cliente com vínculos recusada ("2 equipamentos e 2 ordens de serviço"); exclusão cancelada mantém o cliente; exclusão sem vínculos remove.
- Detalhe do cliente: dados, equipamentos e histórico da mais recente para a mais antiga; identificador inexistente mostra "Cliente não encontrado".
- Equipamentos: número de série duplicado recusado (comparação sem espaços e sem caixa); cadastro válido; filtro por Console; histórico de manutenção em diálogo; troca de cliente com ordens recusada; correção do modelo aceita; exclusão com ordens recusada.
- Ordens: equipamento desabilitado até escolher o cliente e apenas os equipamentos do cliente oferecidos; abertura gera `OS-2026-00127` e redireciona ao detalhe; filtros por status e por técnico.
- Detalhe da OS: percurso completo Recebido → Em análise → Aguardando aprovação → Em reparo → Concluído → Entregue; recusas exibidas para análise sem técnico, aprovação sem diagnóstico, aprovação sem itens, item com valor zero, entrega com saldo de R$ 211,00 e pagamento de R$ 300,00 acima do saldo; orçamento de R$ 120,00 + 2 × R$ 45,50 = R$ 211,00; pagamentos parcial e de quitação; remoção de item com atualização de totais e histórico; cancelamento exige motivo, registra o motivo e deixa apenas "Entregue" como próximo status; técnico travado após cancelamento; ordem entregue sem próximos status; linha do tempo com 12 eventos, data, hora e autor.
- Consulta pública: exibe apenas código, status, equipamento e última atualização.

**Navegador — modo Xano sem contratos:** painel, detalhe da OS e consulta pública exibem a mensagem de integração pendente; nenhum dado de demonstração é exibido.

**Observações e limitações:**
- 1.3: textos com mais de duas casas decimais são recusados (em vez de arredondados) para evitar a ambiguidade de `1.000`; valores calculados são arredondados em centavos.
- 5.1: a reestruturação em `pages/`, `components/` e `state/` foi feita junto com as telas novas, e não em uma etapa isolada sem mudança de comportamento; todas as rotas foram verificadas depois.
- O hot reload do servidor de desenvolvimento recria os dados de demonstração a cada alteração de código (memória por processo).
- Formulários com `reset_on_submit` são limpos também quando a operação é recusada; melhoria de usabilidade para a mudança de frontend.
- No modo Xano, os cartões do painel ficam sem valores (apenas o alerta é exibido); refinamento para a mudança de frontend.
- O indicador de carregamento dos botões não é perceptível no modo demonstração, porque as operações terminam instantaneamente.
- Verificação visual em celular e tablet não realizada nesta mudança (fica para a mudança de frontend e responsividade).

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
