# Integração com o Xano

Este documento descreve a arquitetura de acesso a dados do Assistência TECH, como configurar a fonte de dados Xano e como a aplicação usa o backend em XanoScript da pasta `xano/`.

> **Regra absoluta:** nenhum endpoint, método HTTP, campo, formato de resposta ou fluxo de autenticação do Xano pode ser deduzido ou inventado. Cada contrato registrado em `data/xano/contracts.py` corresponde a um endpoint do contrato-alvo (`tools/xano_target_contract.py`) conferido na documentação publicada com `python -m tools.xano_contract_check`.

## Arquitetura

```
Páginas Reflex (pages/, components/)
        │  exibem dados e disparam eventos
        ▼
Estados Reflex (state/)               carregamento, feedback e erros
        │
        ▼
Serviços de aplicação (services/)     orquestração e permissões
        │  usam as regras puras de domain/ (validação, status, valores, histórico)
        ▼
DataGateway (data/repositories.py)   ← interfaces internas (Protocol)
        │
        ├── Modo demonstração (data/demo/)   dados em memória
        └── Adaptador Xano   (data/xano/)
                 ├── contracts.py   contratos documentados (método, grupo, caminho)
                 ├── client.py      cliente HTTP (httpx), JWT e tradução de erros
                 ├── mappers.py     registros do Xano ⇄ modelos internos
                 ├── base.py        chamada por contrato
                 ├── gateway.py     clientes, equipamentos, técnicos e contas
                 └── orders.py      agregado da OS, consulta pública e portal
```

- As páginas **não** conhecem a fonte de dados, e as regras de negócio valem igualmente para o modo demonstração e para o Xano. O backend em XanoScript repete as regras críticas (perfis, escopo do técnico, transições e pré-condições do status, saldo) para que elas valham também fora da aplicação.
- **Sessão (D12):** o login no Xano devolve um JWT, guardado na sessão do servidor junto com o token opaco do cookie. A cada evento, `AuthService.resolve` coloca o JWT da sessão no contexto da requisição (`data/request_context.py`), e o cliente HTTP envia `Authorization: Bearer`. O JWT nunca chega ao navegador. Um 401 do Xano encerra a sessão.
- **Ordem de serviço (D13):** `save` compara a versão gravada com a nova e envia só as diferenças (`POST/DELETE /os_itens`, `POST /pagamentos`, `PATCH /os_servicos/{id}`, `POST /os_historico`). O código `OS-AAAA-NNNNN` vem do ano de `created_at` e do `id`.
- **Projeções (D14):** a consulta pública usa `GET /consulta_publica/{id}` (sem token) e o portal usa `GET /portal/minha_conta` e `GET /portal/minhas_ordens` (filtrados pelo token no servidor).
- **Contas remotas:** no Xano, o técnico é a própria conta com perfil técnico (o id do técnico é o id da conta) e o autocadastro cria cliente e conta numa só chamada (`POST /auth/signup_cliente`). O gateway declara `remote_accounts=True`, e os serviços seguem esse caminho.

## Configuração

| Variável | Valores | Padrão |
|---|---|---|
| `ASSISTENCIA_DATA_SOURCE` | `demo` ou `xano` | `demo` |
| `XANO_BASE_URL` | endereço da instância, sem `/api:...` | obrigatório com `xano` |
| `XANO_GROUP_AUTH` | identificador do grupo de autenticação | `assistencia-tech-auth` |
| `XANO_GROUP_CLIENTE` | identificador do grupo de clientes | `assistencia-tech-cliente` |
| `XANO_GROUP_OS` | identificador do grupo de ordens de serviço | `assistencia-tech-os` |
| `XANO_TIMEOUT_SECONDS` | número positivo de segundos | `10` |

Nenhuma credencial é configurada: cada usuário entra com a própria conta do Xano. Veja o modelo em `.env.example`. No PowerShell, para a sessão atual:

```powershell
$env:ASSISTENCIA_DATA_SOURCE = "xano"
$env:XANO_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io"
.venv\Scripts\reflex.exe run
```

Para voltar ao modo demonstração: `Remove-Item Env:ASSISTENCIA_DATA_SOURCE`.

### Comportamentos garantidos

- Sem configuração, a aplicação usa o **modo demonstração**, identificado em todas as páginas administrativas.
- Com `xano` sem `XANO_BASE_URL`, a interface informa a configuração incompleta e **não** usa os dados de demonstração no lugar.
- Uma operação sem contrato registrado informa que a integração está pendente e **nenhuma requisição é enviada**.
- Uma chamada que exige login, feita sem JWT na sessão, é recusada antes de sair da aplicação.

## Tradução de falhas HTTP

| Situação | Erro interno | Mensagem ao usuário |
|---|---|---|
| 400, 422 | `ValidationError` | mensagem da pré-condição ou "dados inválidos" |
| 401 | `AuthenticationError` | sessão inválida (a sessão é encerrada) |
| 403 | `PermissionDeniedError` | mensagem da pré-condição ou "sem permissão" |
| 404 | `NotFoundError` | mensagem da pré-condição ou "não encontrado" |
| 408, 429, 5xx, tempo limite, falha de conexão | `ServiceUnavailableError` | serviço indisponível |
| outros | `UnexpectedError` | erro inesperado |

**Mensagens do servidor (D15):** só são exibidas as mensagens das pré-condições do backend em XanoScript, que o Xano devolve com `"payload": ""` (por exemplo, "Já existe um cliente com este CPF."). Erros nativos do Xano, em inglês e com `payload` objeto ou ausente (por exemplo, "Missing param: Cpf"), ficam apenas no log; o usuário vê a mensagem padrão em português.

O cliente HTTP valida os certificados com o repositório do sistema operacional (`truststore`), porque nesta máquina a cadeia do Xano não é reconhecida pelo certifi. A verificação nunca é desligada.

## Como acrescentar um contrato

1. Implemente o endpoint em `xano/` (XanoScript), valide pelo Developer MCP e envie com `xano workspace push` após a simulação (`--dry-run`).
2. Acrescente o endpoint ao contrato-alvo (`tools/xano_target_contract.py` e `docs/XANO_BACKEND_SPEC.md`) e confirme `OK` com `python -m tools.xano_contract_check`.
3. Registre a operação interna em `OPERATIONS` e o contrato em `CONTRACTS` (`data/xano/contracts.py`).
4. Faça o mapeamento em `mappers.py` e use-o no repositório.
5. Escreva testes com `httpx.MockTransport` usando registros no formato documentado (`tests/test_xano_repositories.py`).

O teste `test_every_operation_has_a_contract_from_the_target` impede registrar um contrato que não esteja no contrato-alvo verificado.

## Testes

```powershell
.venv\Scripts\python.exe -m pytest
```

- `tests/test_config.py`: leitura e validação das variáveis.
- `tests/test_factory.py`: escolha da fonte, sem substituição pela demonstração.
- `tests/test_xano.py`: cliente HTTP, JWT, tradução de erros, regra das mensagens do servidor e contratos.
- `tests/test_xano_repositories.py`: mapeamento, sessão com JWT, autocadastro, paginação, agregado da OS, consulta pública e portal sobre um servidor simulado.
- `tests/test_xano_contract_check.py`: verificador do contrato-alvo.

## Limitações conhecidas

- **Limite do plano gratuito do Xano: 10 requisições a cada 20 segundos.** O cliente HTTP reaproveita por 15 segundos as leituras idênticas do mesmo usuário (qualquer escrita limpa o cache), espaça as requisições para respeitar o limite e, se receber 429, espera a janela e tenta uma vez de novo (`data/xano/limits.py`). Por isso algumas telas podem demorar alguns segundos, e uma alteração feita por outro usuário pode levar até 15 segundos para aparecer. Indisponibilidade do Xano não encerra a sessão: a tela mostra a mensagem de serviço indisponível.

- No modo demonstração, os dados são compartilhados por todas as abas e usuários conectados ao mesmo processo e se perdem ao reiniciar a aplicação.
- As sessões ficam na memória do processo: reiniciar a aplicação exige novo login (os dados do Xano não são afetados).
- O tipo de aparelho cadastrado fora da lista da aplicação (por exemplo, pelo painel do Xano) é exibido como "Outro".
