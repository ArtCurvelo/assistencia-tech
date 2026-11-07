# Prompts para a IA do Xano criar o backend

Use estes prompts no assistente de IA do Xano, **na sua própria conta**, para criar o backend conforme `docs/XANO_BACKEND_SPEC.md`. Envie **uma etapa por vez**, revise o que a IA criou e só então siga para a próxima. Pedidos menores dão resultados mais precisos.

**Antes de começar**

- Crie um workspace novo (por exemplo, "Assistência TECH") para não misturar com outros projetos.
- Não cadastre dados reais (CPF, e-mail, telefone de pessoas). Use só dados de teste.
- Ao final, confira tudo com o verificador (seção "Depois de criar").

---

## Etapa 0 — Contexto (envie primeiro)

```text
Vou construir o backend de um sistema de assistência técnica chamado Assistência TECH. Um frontend em Python já existe e vai consumir esta API, por isso os nomes de tabelas, campos, endpoints e valores de enum precisam ser EXATAMENTE os que eu informar, com a mesma grafia, maiúsculas e minúsculas. Não renomeie, não traduza e não acrescente campos obrigatórios que eu não pedir.

Regras gerais para tudo o que for criado:
1. Toda resposta de endpoint deve ter o formato documentado na aba Response, para que a documentação Swagger/OpenAPI mostre os campos.
2. Endpoints marcados como "protegido" exigem autenticação (usuário da tabela user) e respondem 401 sem token válido.
3. Erros de validação respondem 400 com uma mensagem em português no campo "message".
4. Nunca retorne o campo password em nenhuma resposta.
5. A documentação da API (Swagger) de cada grupo deve ficar habilitada e acessível.

Confirme que entendeu. Nas próximas mensagens enviarei as etapas.
```

## Etapa 1 — Tabelas

```text
Crie (ou ajuste) as tabelas abaixo exatamente com estes campos e tipos:

1. Tabela "user" (tabela de autenticação):
   - name (text), email (email, único), password (password)
   - role (enum: admin, atendente, tecnico, cliente), padrão "cliente"
   - cliente_id (referência à tabela cliente, opcional)
   - especialidade (text, opcional)
   - ativo (boolean, padrão true)

2. Tabela "cliente":
   - Nome (text, obrigatório)
   - Cpf (text, único, somente os 11 dígitos)
   - email (email, único)
   - telefone_Aparelho (text, telefone do cliente)

3. Tabela "item_cliente" (aparelhos do cliente):
   - cliente_id (referência à tabela cliente, obrigatório)
   - aparelho (text: Computador, Notebook, Console, Celular, Tablet ou Outro)
   - marca (text), modelo (text), numero_serie (text), observacoes (text)

4. Tabela "os_servicos" (ordens de serviço):
   - cliente_id (referência a cliente, obrigatório)
   - item_cliente_id (referência a item_cliente, obrigatório)
   - user_id (referência a user, opcional: é o técnico responsável)
   - descricao_problema (text, obrigatório)
   - diagnostico (text), motivo_cancelamento (text)
   - status (enum: recebido, em_analise, aguardando_aprovacao, em_reparo, concluido, entregue, cancelado), padrão "recebido"
   - atualizado_em (timestamp)

5. Tabela "os_itens" (itens do orçamento da ordem):
   - os_servicos_id (referência a os_servicos, obrigatório)
   - tipo (enum: servico, peca)
   - descricao (text, obrigatório)
   - quantidade (integer, mínimo 1, padrão 1)
   - valor_unitario (decimal, maior que zero)

6. Tabela "os_historico" (histórico da ordem, somente inclusão):
   - os_servicos_id (referência a os_servicos, obrigatório)
   - autor (text), tipo (text), descricao (text), para_status (text, opcional)

7. Tabela "pagamento":
   - os_servicos_id (referência a os_servicos, obrigatório)
   - valor_a_ser_pago (decimal, maior que zero)
   - forma_de_pagamento (text: Dinheiro, PIX, Cartão de débito ou Cartão de crédito)
   - data_do_pagamento (date)

Todas as tabelas mantêm os campos padrão id e created_at.
```

## Etapa 2 — Grupo de API "Autenticação"

```text
No grupo de API de autenticação, crie ou ajuste estes endpoints:

1. POST /auth/login (público). Entrada: email, password. Resposta: authToken, user_id. Recuse com 401 se o usuário tiver ativo = false.

2. GET /auth/me (protegido). Resposta: id, name, email, role, cliente_id, especialidade, ativo.

3. POST /auth/signup_cliente (público). Entrada: Nome, Cpf, email, telefone_Aparelho, password. Em uma única transação: crie o registro em "cliente" e o usuário em "user" com role = cliente, cliente_id = id do cliente criado e name = Nome. Responda 400 se o Cpf ou o email já existirem. Resposta: authToken, user_id.

4. GET /usuarios (protegido, somente role admin). Resposta: lista com id, name, email, role, cliente_id, especialidade, ativo.

5. POST /usuarios (protegido, somente role admin). Entrada: name, email, password, role, especialidade. Resposta: o usuário criado (sem password). 400 se o email já existir.

6. PATCH /usuarios/{user_id} (protegido, somente role admin). Entrada: name, role, especialidade, ativo e password (opcional; se vier vazio, não altere a senha). Resposta: o usuário atualizado (sem password).

7. GET /tecnicos (protegido, roles admin, atendente ou tecnico). Resposta: lista com id, name, especialidade, ativo dos usuários com role = tecnico.

Se existir um endpoint público /auth/signup que cria usuários sem vínculo, remova-o ou restrinja-o a admin.
```

## Etapa 3 — Grupo de API "Cliente"

```text
Crie um grupo de API "Cliente". Todos os endpoints são protegidos e permitidos para as roles admin, atendente e tecnico (recuse role cliente com 403), exceto onde indicado "somente admin".

1. GET /cliente. Entrada (query): busca (texto opcional, procura em Nome, Cpf, email e telefone_Aparelho), page, per_page. Resposta: objeto paginado com "items" (lista de clientes com id, created_at, Nome, Cpf, email, telefone_Aparelho).
2. POST /cliente. Entrada: Nome, Cpf, email, telefone_Aparelho. 400 se Cpf ou email já existirem. Resposta: o cliente criado.
3. GET /cliente/{cliente_id}. Resposta: o cliente.
4. PATCH /cliente/{cliente_id}. Entrada: Nome, Cpf, email, telefone_Aparelho. Mesmas regras de unicidade. Resposta: o cliente atualizado.
5. DELETE /cliente/{cliente_id} (somente admin).
6. GET /item_cliente. Resposta: lista com id, cliente_id, aparelho, marca, modelo, numero_serie, observacoes.
7. POST /item_cliente. Entrada: cliente_id, aparelho, marca, modelo, numero_serie, observacoes. Resposta: o aparelho criado.
8. GET /item_cliente/{item_cliente_id}. Resposta: o aparelho.
9. PATCH /item_cliente/{item_cliente_id}. Entrada: os mesmos campos do POST. Resposta: o aparelho atualizado.
10. DELETE /item_cliente/{item_cliente_id} (somente admin).
```

## Etapa 4 — Grupo de API "Ordens de Serviço"

```text
Crie um grupo de API "Ordens de Serviço" com estes endpoints. "Colaboradores" significa roles admin, atendente e tecnico.

1. GET /os_servicos (protegido, colaboradores). Resposta: lista de ordens com id, created_at, atualizado_em, cliente_id, item_cliente_id, user_id, descricao_problema, diagnostico, motivo_cancelamento, status, e os addons "_itens" (registros de os_itens da ordem), "_pagamentos" (registros de pagamento da ordem) e "_historico" (registros de os_historico da ordem).
2. GET /os_servicos/{os_servicos_id} (protegido, colaboradores). Resposta: a ordem com os mesmos campos e addons.
3. POST /os_servicos (protegido, admin ou atendente). Entrada: cliente_id, item_cliente_id, descricao_problema, status. Preencha atualizado_em com a data atual. Resposta: a ordem criada.
4. PATCH /os_servicos/{os_servicos_id} (protegido, colaboradores). Entrada: status, user_id, diagnostico, motivo_cancelamento, atualizado_em. Resposta: a ordem atualizada.
5. POST /os_itens (protegido, admin ou tecnico). Entrada: os_servicos_id, tipo, descricao, quantidade, valor_unitario. Resposta: o item criado.
6. DELETE /os_itens/{os_itens_id} (protegido, admin ou tecnico).
7. POST /os_historico (protegido, colaboradores). Entrada: os_servicos_id, autor, tipo, descricao, para_status. Resposta: o evento criado. Não crie endpoints de edição ou exclusão de histórico.
8. POST /pagamentos (protegido, admin ou atendente). Entrada: os_servicos_id, valor_a_ser_pago, forma_de_pagamento, data_do_pagamento. Resposta: id, os_servicos_id, valor_a_ser_pago, forma_de_pagamento, data_do_pagamento.
9. GET /consulta_publica/{os_servicos_id} (PÚBLICO, sem autenticação). Resposta SOMENTE com: id, status, aparelho e modelo (do item_cliente da ordem) e atualizado_em. Não retorne nome, CPF, e-mail, telefone, valores nem diagnóstico.
10. GET /portal/minhas_ordens (protegido, somente role cliente). Retorne apenas as ordens cujo cliente_id é igual ao cliente_id do usuário autenticado (pegue do token, nunca de um parâmetro), com os mesmos campos e addons do item 1.
```

## Etapa 5 — Revisão final

```text
Revise tudo o que foi criado e confirme, endpoint por endpoint:
1. Os endpoints marcados como protegidos exigem autenticação e verificam a role indicada.
2. Somente /auth/login, /auth/signup_cliente e /consulta_publica/{os_servicos_id} são públicos.
3. Todas as respostas estão definidas na aba Response (nenhuma aparece como objeto vazio na documentação).
4. Nenhuma resposta contém o campo password.
5. A documentação Swagger de cada grupo está habilitada.
Liste os três grupos de API criados com o endereço base de cada um (o trecho depois de "api:").
```

## Primeiro administrador

O cadastro público cria apenas clientes. Para ter o primeiro administrador, crie um usuário pelo `POST /auth/signup_cliente` (ou diretamente na tabela `user`, no painel) e altere o campo `role` dele para `admin` **pelo painel do Xano**. Não crie um endpoint público que permita escolher a role.

## Depois de criar: verificação

Anote o endereço da sua instância (por exemplo, `https://xxxx-xxxx-xxxx.n7.xano.io`) e o código de cada grupo (o trecho depois de `api:`). Em seguida, rode:

```powershell
.venv\Scripts\Activate.ps1
python -m tools.xano_contract_check --instance https://SUA-INSTANCIA.xano.io --auth CODIGO_AUTH --cliente CODIGO_CLIENTE --os CODIGO_OS
```

O verificador lê só a documentação dos grupos e mostra o que ainda falta. Copie as pendências que ele apontar e peça à IA do Xano para corrigi-las (por exemplo: "No endpoint GET /cliente, a resposta não documenta o campo email; ajuste a aba Response."). Repita até chegar a **27 de 27**. Depois disso, me envie a instância e os três códigos para eu fazer a integração na aplicação.
