# Design: Autenticação, perfis de acesso e portal do cliente

## Context

Motivação em `proposal.md`; comportamento em `specs/user-auth`, `specs/access-control` e `specs/customer-portal`.

Estado atual (commit `d833fc2`):

- Os serviços de aplicação (`services/clients.py`, `equipment.py`, `orders.py`) recebem o `DataGateway`; `OrderService` recebe `actor: str`, que hoje vale "Usuário demonstração".
- O estado Reflex parte de `AppState` (fonte de dados, feedback) e `AdminState` (catálogo); as páginas administrativas carregam dados em `on_load`.
- `AuthState` só exibe mensagens demonstrativas; não existe usuário, sessão nem verificação de acesso.
- O Reflex 0.8.28 oferece `rx.Cookie(name, max_age, secure, same_site)` e `rx.redirect`; manipuladores podem retornar eventos de redirecionamento.

## Goals / Non-Goals

**Goals:**

- Uma única fonte de verdade para as permissões, em funções puras testáveis, consultada pela interface e pelos serviços.
- Nenhuma operação de dados executada sem um usuário autenticado e autorizado.
- Autenticação atrás de uma interface interna, substituível pelo Xano quando o contrato existir.

**Non-Goals:**

- Sessões persistentes entre reinícios do servidor ou distribuídas entre processos.
- Proteção do servidor de desenvolvimento contra ataques de rede (HTTPS, cabeçalhos de segurança): fica para a implantação.

## Decisions

### D1. Contas de usuário separadas do cliente

Um novo modelo `UserAccount` (id, nome, e-mail, perfil, `password_hash`, `client_id` opcional, `technician_id` opcional, ativo) fica num `UserRepository` próprio do `DataGateway`. Clientes continuam sendo entidades de negócio; um cliente pode existir sem conta (cadastrado no balcão).

- *Alternativa:* acrescentar senha ao `Client`. Rejeitada: colaboradores não são clientes, e misturar credenciais com dados de negócio amplia a exposição.

### D2. Hash de senha com PBKDF2-SHA256 da biblioteca padrão

`domain/passwords.py` gera `pbkdf2_sha256$<iterações>$<sal>$<hash>` com `hashlib.pbkdf2_hmac`, sal de 16 bytes de `secrets`, 600.000 iterações (recomendação OWASP para PBKDF2-SHA256) e comparação com `hmac.compare_digest`. O número de iterações faz parte do valor armazenado, o que permite aumentá-lo no futuro. Os testes usam menos iterações para manter a suíte rápida.

- *Alternativa:* `bcrypt`/`argon2`. Rejeitadas por exigirem dependências nativas; PBKDF2 atende ao requisito sem novas dependências no Windows.

Como cada hash leva cerca de 0,5 s, os usuários de demonstração têm hashes **precalculados** no seed; as senhas de teste ficam documentadas no próprio `seed.py` e em `docs/DEMO_USERS.md`, sempre identificadas como de demonstração.

### D3. Sessões no servidor com token opaco

`data/sessions.py` mantém, em memória, `token → Session(user_id, created_at, last_seen_at)`. O token tem 32 bytes de `secrets.token_urlsafe`. O navegador guarda só o token, em `rx.Cookie("assistencia_sessao", same_site="strict", max_age=8h)`. A cada uso, a sessão expirada por inatividade (2 h) é descartada, e a atividade renova `last_seen_at`. O logout remove o token no servidor e limpa o cookie.

- *Alternativa:* JWT assinado no navegador. Rejeitada: exigiria gerenciar segredos de assinatura e não permitiria revogar a sessão no logout sem uma lista de bloqueio.

O cookie não pode ser `HttpOnly`, porque o Reflex lê cookies pelo cliente. O risco é mitigado por `SameSite=Strict`, pelo token opaco revogável e pela expiração; está registrado em Riscos.

### D4. Limitador de tentativas

`domain/login_throttle.py` registra as falhas por e-mail normalizado numa janela de 15 minutos; com 5 falhas, bloqueia por 5 minutos. O relógio é injetado para os testes. O limitador fica em memória no processo, como as sessões.

### D5. Permissões como dados

`domain/permissions.py` define o `Role` (StrEnum), o `Permission` (StrEnum com nomes como `clients.manage`, `orders.diagnose`, `orders.status.technical`) e `ROLE_PERMISSIONS: dict[Role, frozenset[Permission]]`, que é a matriz da proposta. Funções puras:

- `has_permission(principal, permission) -> bool`
- `require(principal, permission)`, que lança `PermissionDeniedError`
- `status_permission(current, target) -> Permission`, que mapeia cada transição para a permissão técnica ou de atendimento
- `ensure_can_modify_order(principal, order)`, que aplica o escopo do técnico

`Principal` é um objeto imutável (id, nome, perfil, `client_id`, `technician_id`) derivado do `UserAccount` e exposto à interface sem o hash.

### D6. Autorização dentro dos serviços

Os serviços passam a receber `principal: Principal` no construtor (`ClientService(gateway, principal)`, etc.) e chamam `require(...)` no início de cada método. `OrderService` usa `principal.display_name` ("Carlos Mendes (Técnico)") como autor do histórico, substituindo o `actor` fixo. Novos erros na hierarquia: `AuthenticationError` (sem sessão ou sessão expirada) e `PermissionDeniedError` (perfil sem permissão).

### D7. Estado e guarda de rotas

- `AppState` ganha `session_token: str = rx.Cookie(...)` e os auxiliares `_principal()` e `_require_principal()`.
- `SessionState(AppState)` expõe ao frontend `user_name`, `user_role` e `permissions: list[str]`, além de vars derivadas (`can_manage_clients`, etc.) usadas por menus e botões.
- Cada `on_load` administrativo começa com `self._guard(permission)`, que retorna `rx.redirect("/login?proximo=<rota>")` sem sessão ou `rx.redirect("/acesso-negado")` sem permissão; só depois carrega os dados. Isso garante que nenhum dado é enviado ao navegador antes da verificação.
- O parâmetro `proximo` só aceita caminhos internos que começam com `/` e não com `//`, evitando redirecionamento aberto.

### D8. Portal do cliente

`services/portal.py` oferece `my_orders(principal)` e `my_order(principal, code)`. Ambos filtram por `principal.client_id` e lançam `NotFoundError` para ordens de outro cliente, sem revelar a existência delas. A projeção do portal omite autores e técnicos do histórico e mostra só os eventos de status.

### D9. Autenticação no Xano

`AuthProvider` (Protocol com `authenticate`, `register_client`, `get_user`) tem duas implementações: a de demonstração (repositório de usuários e hashes locais) e a Xano, cujas operações `auth.login`, `auth.register` e `auth.me` entram em `OPERATIONS` sem contrato. No modo Xano, o login informa que a autenticação aguarda a documentação oficial, sem enviar requisições.

### D10. Interface

- Menu público: "Entrar" e "Criar conta" para visitantes; para usuários autenticados, "Minha área" (painel ou portal) e "Sair". O link "Painel" deixa de aparecer para visitantes.
- Barra lateral: itens conforme as permissões, mais o bloco do usuário com nome, perfil e "Sair".
- Botões e formulários de ações não permitidas ficam ocultos; o seletor de status oferece só as transições que o perfil pode executar.
- Login no modo demonstração: cartões de acesso rápido por perfil, que preenchem e enviam as credenciais de teste.

## Risks / Trade-offs

- [Cookie legível por JavaScript (sem `HttpOnly`)] → `SameSite=Strict`, token opaco revogável, expiração por inatividade e nenhuma informação sensível no cookie; documentado como limitação do framework.
- [Sessões e bloqueios em memória somem ao reiniciar o servidor] → aceitável para a demonstração; os usuários precisam entrar de novo.
- [Senhas de demonstração conhecidas] → só existem no modo demonstração, claramente identificadas, e não são aceitas em nenhuma integração real.
- [Hash lento no cadastro e no login (~0,5 s)] → custo intencional contra força bruta; o botão mostra o carregamento.

## Migration Plan

1. Entram o domínio (senhas, permissões, limitador) e os serviços de autenticação, com testes.
2. Os serviços existentes passam a exigir `Principal`; os testes são atualizados para usar usuários de cada perfil.
3. A interface recebe as guardas, os menus por perfil, o login, o cadastro, o portal e a página de acesso negado.
4. Rollback: reverter o commit da mudança restaura o acesso livre anterior.
