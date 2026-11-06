# Integração com o Xano

Este documento descreve a arquitetura de acesso a dados do Assistência TECH, como configurar a fonte de dados e como registrar os contratos oficiais da API do Xano quando a documentação for fornecida.

> **Regra absoluta:** nenhum endpoint, método HTTP, campo, formato de resposta ou fluxo de autenticação do Xano pode ser deduzido ou inventado. Tudo o que for registrado precisa vir da documentação oficial do workspace (Swagger/OpenAPI do API group).

## Arquitetura

```
Páginas Reflex (pages/, components/)
        │  exibem dados e disparam eventos
        ▼
Estados Reflex (state/)               carregamento, feedback e erros
        │
        ▼
Serviços de aplicação (services/)     orquestração
        │  usam as regras puras de domain/ (validação, status, valores, histórico)
        ▼
DataGateway (data/repositories.py)   ← interfaces internas (Protocol)
        │
        ├── Modo demonstração (data/demo/)   dados em memória
        └── Adaptador Xano   (data/xano/)
                 ├── contracts.py   registro de contratos documentados
                 ├── client.py      cliente HTTP (httpx) + tradução de erros
                 └── gateway.py     implementação das interfaces
```

- As páginas **não** conhecem a fonte de dados, e as regras de negócio valem igualmente para o modo demonstração e para o Xano.
- `data/factory.py` escolhe o gateway a partir da configuração.
- Os modelos (`models/`) validam os dados de entrada e geram mensagens em português.
- Os erros (`data/errors.py`) carregam uma mensagem segura para o usuário (`user_message`) e detalhes técnicos apenas para o log (`detail`).

## Configuração

| Variável | Valores | Padrão |
|---|---|---|
| `ASSISTENCIA_DATA_SOURCE` | `demo` ou `xano` | `demo` |
| `XANO_BASE_URL` | endereço base do API group | obrigatório com `xano` |
| `XANO_TIMEOUT_SECONDS` | número positivo de segundos | `10` |

Veja o modelo em `.env.example`. No PowerShell, para a sessão atual:

```powershell
$env:ASSISTENCIA_DATA_SOURCE = "xano"
$env:XANO_BASE_URL = "https://exemplo.invalid/api"   # substitua pelo endereço oficial
.venv\Scripts\reflex.exe run
```

Para voltar ao modo demonstração: `Remove-Item Env:ASSISTENCIA_DATA_SOURCE`.

### Comportamentos garantidos

- Sem configuração, a aplicação usa o **modo demonstração**, identificado em todas as páginas administrativas.
- Com `xano` sem `XANO_BASE_URL`, a interface informa a configuração incompleta e **não** usa os dados de demonstração no lugar.
- Com `xano` e sem contratos registrados, cada operação informa que a integração aguarda a documentação oficial e **nenhuma requisição é enviada**.

## Tradução de falhas HTTP

| Situação | Erro interno | Mensagem ao usuário |
|---|---|---|
| 400, 422 | `ValidationError` | dados inválidos |
| 401, 403 | `UnauthorizedError` | acesso não autorizado |
| 404 | `NotFoundError` | registro não encontrado |
| 408, 429, 5xx, tempo limite, falha de conexão | `ServiceUnavailableError` | serviço indisponível |
| outros | `UnexpectedError` | erro inesperado |

A classificação usa apenas o código de status, pois o formato do corpo de erro do Xano ainda não foi documentado.

## Como registrar um contrato (quando a documentação chegar)

1. Obtenha a documentação oficial do API group (no Xano, cada API group disponibiliza sua especificação Swagger/OpenAPI).
2. Para cada operação interna listada em `data/xano/contracts.py` (`OPERATIONS`), localize o endpoint correspondente **na documentação**.
3. Adicione a entrada em `CONTRACTS` com `method`, `path` e `source` (a referência exata da documentação, por exemplo a seção do Swagger).
4. Implemente o mapeamento entre a resposta documentada e o modelo interno em `data/xano/gateway.py` (tarefa 6.2 da mudança `integrate-xano-backend`).
5. Escreva testes com `httpx.MockTransport` usando exemplos de resposta copiados da documentação.
6. Atualize `tasks.md` da mudança com a evidência da verificação.

O teste `test_contract_registry_starts_empty` existe para impedir que contratos sejam adicionados sem esse processo. Ao registrar o primeiro contrato documentado, substitua-o por testes do contrato real.

## Testes

```powershell
.venv\Scripts\python.exe -m pytest
```

- `tests/test_config.py`: leitura e validação das variáveis.
- `tests/test_models.py`: validação e mensagens.
- `tests/test_demo_gateway.py`: comportamento do modo demonstração.
- `tests/test_factory.py`: escolha da fonte, sem substituição pela demonstração.
- `tests/test_xano.py`: cliente HTTP, tradução de erros e garantia de nenhuma requisição sem contrato.

## Limitações conhecidas

- No modo demonstração, os dados são compartilhados por todas as abas e usuários conectados ao mesmo processo e se perdem ao reiniciar a aplicação.
- Autenticação com o Xano depende do contrato oficial e ainda não foi implementada.
