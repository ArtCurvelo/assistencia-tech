# Tasks

## 1. Backend

- [x] 1.1 Campo `anonimizado` em `cliente` e `POST /portal/excluir_conta`; validar pelo Developer MCP, simular e enviar após autorização.

## 2. Aplicação

- [x] 2.1 `Client.anonymized`, leitura de cadastro anonimizado, `PortalRepository.delete_account` (demonstração e Xano), `PortalService.export_data` e `delete_account`; testes.
- [x] 2.2 Painel "Privacidade e dados (LGPD)" no portal com download e diálogo de exclusão.

## 3. Verificação

- [x] 3.1 `pytest`, `openspec validate --strict`, verificador de contrato, roteiro no Xano real com um cliente de vitrine sem ordens em andamento, e navegador.

## Registro de verificação (2026-11-13)

- **pytest:** 6 testes novos em `tests/test_lgpd.py`; ponta a ponta: painel de privacidade e download dos dados (`e2e/test_site.py`).
- **XanoScript:** 64 arquivos válidos no Developer MCP; simulação com `ADD_FIELD cliente` e `CREATE query portal/excluir_conta POST`; envio após autorização.
- **Xano real** (clientes de vitrine):
  - senha errada → 403 "Senha incorreta."; cliente com ordem em andamento → 400 "Você tem ordens em andamento…"; atendente → 403;
  - exclusão do cliente de vitrine Thiago Barros → 200; novo login → 403 "E-mail ou senha inválidos."; token antigo → 403 "Conta inativa.";
  - cadastro visto pela equipe: "Cliente anonimizado", CPF e e-mail substituídos por marcadores, telefone vazio, `anonimizado: true`;
  - a ordem entregue continua ligada ao cadastro, com a nota 9 e o comentário apagado.
- **Dado de vitrine consumido:** o cliente Thiago Barros ficou anonimizado de forma definitiva.
