# Análise dos contratos do Xano

Levantamento feito em 06/11/2026 a partir da documentação OpenAPI publicada pelo próprio Xano para cada API group (`/apispec:<grupo>?type=json`). As cópias estão em `docs/xano-openapi/`. Nenhum endpoint de dados foi chamado; apenas a documentação foi lida.

| Grupo | Base | Documentação |
|---|---|---|
| Autenticação | `api:GRUPO-AUTH-COLEGA` | obtida (12 operações) |
| Cliente | `api:GRUPO-CLIENTE-COLEGA` | obtida (15 operações) |
| Ordens de Serviço | `api:GRUPO-OS-COLEGA` | obtida (29 operações) |
| Sistema de Gestão | `api:GRUPO-GESTAO-COLEGA` | **indisponível** (HTTP 403: "Access to this resource is restricted") |

## 1. Alertas antes de qualquer integração

1. **Endpoints sem autenticação.** Nenhuma das 15 operações de Cliente nem das 29 de Ordens de Serviço declara `bearerAuth`. Pela documentação, qualquer pessoa com a URL pode listar, alterar e excluir clientes (incluindo CPF), aparelhos, ordens, pagamentos e peças. Recomenda-se exigir autenticação nesses endpoints no Xano antes de ligar a aplicação. Isso também é condição da LGPD para dados pessoais.
2. **Respostas sem esquema.** `GET /cliente` (busca paginada), `GET /os_servicos/{id}` (detalhe com totais), `GET /dashboard`, `POST /pecas`, `POST /adicionar_pecas_os`, `POST /pagamentos` e `PATCH /pagamentos/{id}/quitar` documentam a resposta como objeto vazio (`{}`). Sem o formato da resposta não é possível mapeá-las sem adivinhar, o que a regra do projeto proíbe.
3. **Grupo "Sistema de Gestão" sem documentação acessível.** Seus endpoints não podem ser usados até a documentação ser liberada ou exportada.

## 2. Comparação com o modelo da aplicação

### Autenticação e perfis

| Aplicação | Xano | Situação |
|---|---|---|
| Login por e-mail e senha | `POST /auth/login` → `authToken`, `user_id` | compatível |
| Conta do usuário | `GET /auth/me` → `id, name, email, role` | compatível em parte |
| Perfis Administrador, Atendente, Técnico, Cliente | `role`: `admin` ou `member` | **incompatível**: não há como distinguir atendente, técnico e cliente |
| Conta de cliente ligada ao cadastro do cliente | `POST /auth/signup` só com `name, email, password` | **ausente**: não há vínculo entre usuário e cliente |
| Técnico vinculado à conta | — | **ausente** (o `user_id` da OS pode ser o técnico, mas não está documentado) |
| Gestão de colaboradores (ativar/desativar, cargo) | — (talvez em "Sistema de Gestão") | sem contrato |

### Clientes (`/cliente`, `/endercecos`)

| Aplicação | Xano | Situação |
|---|---|---|
| Nome | `Nome` (obrigatório) | compatível |
| CPF (obrigatório, único) | `Cpf` (opcional; o POST diz validar duplicidade) | compatível em parte |
| Telefone | `telefone_Aparelho` | compatível (nome do campo sugere outro significado; confirmar) |
| **E-mail** (obrigatório, único) | — | **ausente** |
| — | `endercecos` (CEP, logradouro, bairro, cidade) | recurso extra do Xano, ainda não especificado na aplicação |

### Equipamentos (`/item_cliente`)

| Aplicação | Xano | Situação |
|---|---|---|
| Cliente | `cliente_id` | compatível (id inteiro) |
| Tipo | `aparelho` (texto) | compatível |
| Marca (texto livre) | `pecas_marcas_id` (cadastro de marcas) | **diferente**: exige lista de marcas |
| Modelo, número de série | `modelo`, `numero_serie` | compatível |
| Observações | — | ausente |

### Ordens de serviço (`/os_servicos`, `/servico`, `/pagamento`, `/pecas`)

| Aplicação | Xano | Situação |
|---|---|---|
| Código `OS-AAAA-NNNNN` | `id` inteiro | diferente (o código pode ser gerado a partir do `id`) |
| 7 status com transições e pré-condições | `status`: `aberta`, `em_andamento`, `aguardando_peca`, `concluida`, `cancelada` | **incompatível**: não há "aguardando aprovação" nem "entregue"; existe "aguardando peça" |
| Técnico responsável | `user_id` | provável, não documentado |
| Problema relatado | `descricao_problema` | compatível |
| Diagnóstico | `S_desc`? | **indefinido**: o significado não está documentado |
| Orçamento: vários serviços e peças avulsas | 1 serviço por OS (`nome_servico`, `valor_do_servico`) + peças do estoque (`/adicionar_pecas_os`, com baixa no estoque) | **diferente**: peças vêm do catálogo com estoque, e só há um serviço |
| Pagamentos parciais com forma e data | `/pagamentos` (`servico_id`, `valor_a_ser_pago`, `forma_de_pagamento`, `data_do_pagamento`, pendente/quitado) | diferente: `servico_id` aponta para a tabela `servico` ou para `os_servicos`? não documentado |
| Histórico imutável com autor | — | **ausente** |
| Cancelamento com motivo | — | ausente |
| — | `servico` (data de início, entrega, valor de entrega) | recurso do Xano sem correspondência clara com `os_servicos` |
| — | estoque de peças, marcas, dashboard | recursos extras do Xano |

## 3. Conclusão

O backend do Xano e a aplicação foram modelados de forma diferente em pontos centrais: perfis, e-mail do cliente, ciclo de status, orçamento, histórico e vínculo entre conta e cliente. Também há partes sem esquema documentado. Uma integração completa exige decidir qual modelo prevalece:

- **A — Ajustar o Xano ao modelo especificado** (recomendado). As specs, os testes e as regras atuais são mantidos; o Xano recebe os campos e tabelas que faltam. A lista de ajustes está na seção 4.
- **B — Ajustar a aplicação ao modelo do Xano.** Exige reescrever specs e remover ou alterar funcionalidades já verificadas: 7 → 5 status, sem entrega condicionada à quitação, sem e-mail do cliente, perfis reduzidos a admin/member, orçamento com um único serviço.
- **C — Integração parcial imediata.** Ligar já o que é compatível e documentado (login e `auth/me`, cadastro e edição de clientes sem e-mail, aparelhos), mantendo ordens e perfis no modo demonstração. Isso cria um sistema com duas fontes de dados e exige regras para não misturar dados reais e fictícios.

## 4. Ajustes sugeridos no Xano (opção A)

1. Exigir `bearerAuth` em todos os endpoints de Cliente e Ordens de Serviço.
2. Definir o formato de resposta (aba *Response* no Xano) de `GET /cliente`, `GET /os_servicos/{id}`, `GET /dashboard`, `POST /pecas`, `POST /adicionar_pecas_os`, `POST /pagamentos` e `PATCH /pagamentos/{id}/quitar`.
3. Liberar ou exportar a documentação do grupo "Sistema de Gestão".
4. `user`: `role` com `admin`, `atendente`, `tecnico`, `cliente`; campos `cliente_id`, `ativo` e `especialidade` (técnico).
5. `cliente`: campo `email` (único); confirmar se `telefone_Aparelho` é o telefone do cliente.
6. `os_servicos`: status `recebido`, `em_analise`, `aguardando_aprovacao`, `em_reparo`, `concluido`, `entregue`, `cancelado`; campos `diagnostico`, `motivo_cancelamento`; confirmar que `user_id` é o técnico.
7. Itens de orçamento: tabela de itens da OS (tipo serviço/peça, descrição, quantidade, valor unitário). Ela pode conviver com o estoque de peças.
8. Histórico: tabela de eventos da OS (data, autor, tipo, descrição, status de destino).
9. Pagamentos: confirmar que `servico_id` referencia `os_servicos`.

Depois desses ajustes, cada operação interna (`OPERATIONS` em `assistencia_tech/data/xano/contracts.py`) poderá ser registrada com a referência exata do endpoint documentado, e o mapeamento seguirá o grupo 6 de `openspec/changes/integrate-xano-backend/tasks.md`.
