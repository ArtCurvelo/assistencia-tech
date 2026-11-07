# Especificação do backend Xano (opção A)

Este documento descreve os ajustes a fazer no workspace Xano para que a aplicação se integre a ele sem perder funcionalidades. Ele é o **contrato-alvo**: o que a aplicação precisa receber. A mesma definição, em forma de dados, está em `tools/xano_target_contract.py`.

Para criar o backend com a IA do próprio Xano, use os prompts em etapas de `docs/XANO_AI_PROMPTS.md`.

Depois de cada rodada de ajustes no Xano, rode o verificador (para outra instância, informe `--instance`, `--auth`, `--cliente` e `--os`):

```powershell
.venv\Scripts\Activate.ps1
python -m tools.xano_contract_check
```

Ele baixa a documentação publicada pelo Xano (sem chamar endpoints de dados) e mostra `OK` ou o que falta em cada um dos 29 endpoints. O backend foi implementado em XanoScript na pasta `xano/` (workspace 170741, grupos `assistencia-tech-auth`, `assistencia-tech-cliente` e `assistencia-tech-os`). Situação em 07/11/2026: **28 de 28** (inclui `GET /portal/minha_conta`, o *addon* `_aparelho` e `created_at` na consulta pública, acrescentados na integração da aplicação). Cópias da documentação em `docs/xano-openapi/*-assistencia-tech-*.json` (`--offline`).

> **Regras gerais**
> 1. Todo endpoint marcado com **token** deve exigir autenticação (*Authentication: user*) e retornar 401 sem token válido.
> 2. Preencha a aba **Response** de cada endpoint no Xano. Sem isso, a documentação mostra a resposta como `{}` e a aplicação não pode usá-la.
> 3. Erros de validação (CPF ou e-mail duplicado, campo obrigatório) devem retornar **400** com uma mensagem em português no campo `message`.
> 4. Mantenha os nomes de campo exatamente como abaixo. A aplicação converte os nomes; o Xano não precisa conhecer os nomes internos.

## 1. Tabelas

### `user` (grupo Autenticação)

| Campo | Tipo | Observação |
|---|---|---|
| `id` | int | já existe |
| `name`, `email`, `password` | texto / e-mail / senha | já existem |
| `role` | enum `admin`, `atendente`, `tecnico`, `cliente` | **alterar** (hoje: `admin`, `member`) |
| `cliente_id` | int (tabela `cliente`), opcional | **novo**: preenchido só para `role = cliente` |
| `especialidade` | texto, opcional | **novo**: usado para `role = tecnico` |
| `ativo` | booleano, padrão `true` | **novo**: usuário inativo não faz login |

### `cliente` (grupo Cliente)

| Campo | Tipo | Observação |
|---|---|---|
| `Nome`, `Cpf`, `telefone_Aparelho` | texto | já existem (`telefone_Aparelho` = telefone do cliente) |
| `email` | e-mail, **único** | **novo** |
| `Cpf` | texto, **único** | tornar único |

### `item_cliente` (aparelhos)

| Campo | Tipo | Observação |
|---|---|---|
| `cliente_id`, `aparelho`, `modelo`, `numero_serie` | | já existem; `aparelho` recebe o tipo (Computador, Notebook, Console, Celular, Tablet, Outro) |
| `marca` | texto | **novo** (o `pecas_marcas_id` pode continuar para o estoque) |
| `observacoes` | texto | **novo** |

### `os_servicos` (ordens)

| Campo | Tipo | Observação |
|---|---|---|
| `cliente_id`, `item_cliente_id`, `descricao_problema` | | já existem |
| `user_id` | int (`user`), opcional | já existe; passa a significar o **técnico responsável** |
| `status` | enum `recebido`, `em_analise`, `aguardando_aprovacao`, `em_reparo`, `concluido`, `entregue`, `cancelado` | **alterar** |
| `diagnostico` | texto | **novo** |
| `motivo_cancelamento` | texto | **novo** |
| `atualizado_em` | timestamp | **novo** |
| `nome_servico`, `S_desc`, `pecas_id`, `valor_do_servico` | | deixam de ser usados (substituídos por `os_itens`) |

O código exibido (`OS-2026-00127`) é calculado pela aplicação a partir do ano de `created_at` e do `id`.

### `os_itens` (**nova**: itens do orçamento)

`id`, `created_at`, `os_servicos_id` (int), `tipo` (enum `servico`, `peca`), `descricao` (texto), `quantidade` (int ≥ 1), `valor_unitario` (decimal > 0). Opcional: `pecas_id`, se quiser ligar ao estoque.

### `os_historico` (**nova**: histórico da ordem)

`id`, `created_at`, `os_servicos_id` (int), `autor` (texto, por exemplo "Carlos Mendes (Técnico)"), `tipo` (texto), `descricao` (texto), `para_status` (texto, vazio quando não é mudança de status). Sem endpoints de edição ou exclusão: o histórico só cresce.

### `pagamento`

Usar `os_servicos_id` (int) no lugar de `servico_id`, ou confirmar que `servico_id` aponta para `os_servicos`. `valor_a_ser_pago`, `forma_de_pagamento` (Dinheiro, PIX, Cartão de débito, Cartão de crédito) e `data_do_pagamento` já existem.

## 2. Endpoints

Legenda: **público** (sem token) · **token** (qualquer usuário autenticado) · **token: perfis** (verificar o `role` do usuário do token).

### Grupo Autenticação (`api:assistencia-tech-auth`)

| Método e caminho | Acesso | Entrada | Resposta 200 |
|---|---|---|---|
| `POST /auth/login` | público | `email`, `password` | `authToken`, `user_id` (já atende); recusar `ativo = false` |
| `GET /auth/me` | token | — | `id`, `name`, `email`, `role`, `cliente_id`, `especialidade`, `ativo` |
| `POST /auth/signup_cliente` | público | `Nome`, `Cpf`, `email`, `telefone_Aparelho`, `password` | `authToken`, `user_id`. Cria `cliente` e `user` (`role = cliente`, `cliente_id` preenchido) na mesma transação. |
| `GET /usuarios` | token: admin | — | lista de `id`, `name`, `email`, `role`, `cliente_id`, `especialidade`, `ativo` (nunca a senha) |
| `POST /usuarios` | token: admin | `name`, `email`, `password`, `role`, `especialidade` | o usuário criado |
| `PATCH /usuarios/{user_id}` | token: admin | `name`, `role`, `especialidade`, `ativo`, `password` (opcional) | o usuário atualizado |
| `GET /tecnicos` | token: admin, atendente, técnico | — | lista de `id`, `name`, `especialidade`, `ativo` dos usuários com `role = tecnico` |

O `POST /auth/signup` atual cria usuários `member` sem vínculo: remova-o ou restrinja-o a administradores.

### Grupo Cliente (`api:assistencia-tech-cliente`): todos com token (admin, atendente e técnico)

| Método e caminho | Entrada | Resposta 200 |
|---|---|---|
| `GET /cliente` | query `busca`, `page`, `per_page` | objeto com `items` (lista de clientes com `id`, `created_at`, `Nome`, `Cpf`, `email`, `telefone_Aparelho`) e os dados de paginação |
| `POST /cliente` | `Nome`, `Cpf`, `email`, `telefone_Aparelho` | o cliente criado; 400 se o CPF ou o e-mail já existir |
| `GET /cliente/{cliente_id}` | — | o cliente |
| `PATCH /cliente/{cliente_id}` | `Nome`, `Cpf`, `email`, `telefone_Aparelho` | o cliente atualizado |
| `DELETE /cliente/{cliente_id}` | — | somente admin |
| `GET /item_cliente` | — | lista com `id`, `cliente_id`, `aparelho`, `marca`, `modelo`, `numero_serie`, `observacoes` |
| `POST /item_cliente` | `cliente_id`, `aparelho`, `marca`, `modelo`, `numero_serie`, `observacoes` | o aparelho criado |
| `GET /item_cliente/{item_cliente_id}` | — | o aparelho |
| `PATCH /item_cliente/{item_cliente_id}` | os mesmos campos do POST | o aparelho atualizado |
| `DELETE /item_cliente/{item_cliente_id}` | — | somente admin |

### Grupo Ordens de Serviço (`api:assistencia-tech-os`)

| Método e caminho | Acesso | Entrada | Resposta 200 |
|---|---|---|---|
| `GET /os_servicos` | token: colaboradores | — | lista de ordens com os campos de `os_servicos` e os *addons* `_itens`, `_pagamentos`, `_historico` |
| `GET /os_servicos/{os_servicos_id}` | token: colaboradores | — | a ordem com `_itens`, `_pagamentos`, `_historico` |
| `POST /os_servicos` | token: admin, atendente | `cliente_id`, `item_cliente_id`, `descricao_problema`, `status` | a ordem criada |
| `PATCH /os_servicos/{os_servicos_id}` | token: colaboradores | `status`, `user_id`, `diagnostico`, `motivo_cancelamento`, `atualizado_em` | a ordem atualizada |
| `POST /os_itens` | token: admin, técnico | `os_servicos_id`, `tipo`, `descricao`, `quantidade`, `valor_unitario` | o item criado |
| `DELETE /os_itens/{os_itens_id}` | token: admin, técnico | — | — |
| `POST /os_historico` | token: colaboradores | `os_servicos_id`, `autor`, `tipo`, `descricao`, `para_status` | o evento criado |
| `POST /pagamentos` | token: admin, atendente | `os_servicos_id`, `valor_a_ser_pago`, `forma_de_pagamento`, `data_do_pagamento` | o pagamento criado (`id`, `os_servicos_id`, `valor_a_ser_pago`, `forma_de_pagamento`, `data_do_pagamento`) |
| `GET /consulta_publica/{os_servicos_id}` | **público** | — | **somente** `id`, `created_at`, `status`, `aparelho`, `modelo`, `atualizado_em` (`created_at` confere o ano do código) |
| `GET /portal/minhas_ordens` | token: cliente | — | as ordens cujo `cliente_id` é o do usuário do token, com `_itens`, `_pagamentos`, `_historico` e `_aparelho` |
| `GET /portal/minha_conta` | token: cliente | — | o cadastro (`cliente`) vinculado ao usuário do token |
| `POST /portal/decisao_orcamento` | token: cliente | `os_servicos_id`, `aprovar`, `motivo` | a ordem atualizada; somente ordem própria em `aguardando_aprovacao`; recusa exige `motivo`; grava a decisão e o status no histórico numa transação |

**Importante para a privacidade:** o `GET /consulta_publica` não pode devolver nome, CPF, telefone, valores ou diagnóstico. O `GET /portal/minhas_ordens` deve filtrar no servidor pelo `cliente_id` do token, nunca por um parâmetro enviado pelo navegador.

## 3. O que continua na aplicação

As regras de negócio já implementadas e testadas na aplicação continuam valendo sobre os dados do Xano, e o Xano não precisa repeti-las:

- transições de status e suas pré-condições;
- cálculo de valores e quitação antes da entrega;
- matriz de permissões por perfil;
- regras de colaboradores (último administrador, técnico com ordens em aberto);
- relatórios, gráficos e exportação CSV.

O Xano é responsável por autenticação, unicidade (CPF e e-mail), restrição de acesso por token e perfil, e persistência.

## 4. Fora do contrato atual

Estes recursos do Xano não são usados nesta integração e podem continuar como estão: endereços (`endercecos`), estoque e marcas de peças (`pecas`, `pecas_marcas`, `adicionar_pecas_os`, `remover_pecas_os`), `servico`, `dashboard`, permissões (`permiss_es`), redefinição de senha por link mágico e o grupo Sistema de Gestão. O estoque de peças é um bom candidato a uma próxima fase.
