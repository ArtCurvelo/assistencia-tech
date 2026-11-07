# Tasks

## 1. Especificação

- [x] 1.1 Escrever os requisitos e cenários de `backend-integration` para sessão com token, projeções no servidor, mensagens das pré-condições, contas remotas, limite de requisições e contrato conferido; verificar com `openspec validate specify-xano-backend-behavior --strict`.
- [x] 1.2 Ajustar o requisito "Tradução das respostas de erro" (401, 403 e indisponibilidade); verificar com a mesma validação.

## 2. Rastreabilidade com os testes existentes

- [x] 2.1 Associar cada cenário a um teste automatizado ou ao registro da tarefa 6.5 de `2026-11-07-integrate-xano-backend`; verificar executando `pytest` e registrando o resultado neste arquivo.

## 3. Encerramento

- [x] 3.1 Arquivar a mudança e confirmar `openspec validate --all --strict`.

## Registro de verificação (2026-11-07)

- **OpenSpec:** `openspec validate specify-xano-backend-behavior --strict` válido.
- **pytest (.venv):** 357 passed in 61.82s (0:01:01). Acrescentado `test_backend_unavailable_keeps_the_session`, único cenário sem teste automatizado.

| Requisito / cenário | Evidência |
|---|---|
| Sessão: login guarda o token no servidor | `test_login_keeps_jwt_in_the_server_session` |
| Sessão: sem token na sessão | `test_authenticated_request_without_token_sends_nothing` |
| Sessão: token recusado pelo backend | `test_backend_401_ends_the_session` |
| Projeções: consulta pública sem dados pessoais | `test_public_lookup_needs_no_token_and_hides_personal_data`; roteiro 6.5 |
| Projeções: código com ano errado | `test_get_by_code_checks_the_year`; `test_public_lookup_needs_no_token_and_hides_personal_data` |
| Projeções: portal filtrado pelo token | `test_portal_uses_server_side_projections`; roteiro 6.5 |
| Projeções: token de cliente em endpoint de colaborador | roteiro 6.5 (403 do Xano em `cliente`, `os_servicos` e `usuarios`) |
| Mensagens: regra recusada pelo backend | `test_precondition_messages_are_shown`; `test_duplicate_cpf_message_comes_from_the_backend` |
| Mensagens: erro técnico do Xano | `test_native_xano_errors_never_reach_the_user`; `test_server_message_rule` |
| Contas: cadastro de técnico | `test_staff_technician_is_created_as_an_account`; roteiro 6.5 |
| Contas: autocadastro de cliente | `test_signup_creates_client_and_account_in_one_call`; roteiro 6.5 |
| Limite: muitas leituras seguidas | `test_pacer_waits_when_the_window_is_full`; `test_429_waits_for_the_window_and_retries_once` |
| Limite: leitura após uma alteração | `test_reads_are_cached_per_token_and_writes_clear_the_cache` |
| Limite: backend indisponível | `test_backend_unavailable_keeps_the_session`; `test_repeated_429_is_service_unavailable` |
| Contrato: verificação do contrato | `test_own_backend_snapshots_meet_the_whole_target`; `python -m tools.xano_contract_check` (28 de 28) |
| Contrato: contrato fora do alvo | `test_every_operation_has_a_contract_from_the_target` |
| Erros: recurso inexistente / erro interno | `test_native_xano_errors_never_reach_the_user` (404 e 5xx) |
| Erros: sessão inválida | `test_native_xano_errors_never_reach_the_user` (401); `test_backend_401_ends_the_session` |
| Erros: acesso negado | `test_precondition_messages_are_shown` (403) |
