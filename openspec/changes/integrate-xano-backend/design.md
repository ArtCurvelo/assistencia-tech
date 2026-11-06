# Design: Integração do backend Xano

## Context

Motivação em `proposal.md`; comportamento esperado em `specs/data-source` e `specs/backend-integration`.

Estado atual observado (Fase 0, 2026-11-06):

- `assistencia_tech/state.py` contém um único `AppState` que guarda clientes, equipamentos e ordens como `list[dict[str, str]]` iniciadas por `services/demo_data.py`, e implementa diretamente cadastro, busca e mudança de status.
- Validações falham em silêncio (`return` sem mensagem) e o contador de ordens gera `OS-2026-126` enquanto os dados iniciais usam `OS-2026-00125`.
- Não existe nenhum código de comunicação HTTP. A documentação oficial da API do Xano ainda não foi fornecida.
- Ambiente: Reflex 0.8.28 na `.venv`, Python 3.14, `httpx` 0.28 e `pydantic` 2 já instalados como dependências do Reflex.

## Goals / Non-Goals

**Goals:**

- Os componentes e o estado Reflex dependem apenas de interfaces internas; trocar a fonte de dados não exige alterar páginas.
- O modo demonstração e o adaptador Xano obedecem às mesmas interfaces e passam pelos mesmos testes de contrato interno.
- O cliente Xano é testável sem rede.

**Non-Goals:**

- Definir o modelo de dados definitivo (campos de diagnóstico, peças, pagamentos e histórico pertencem a uma mudança posterior de domínio).
- Supor o formato dos corpos de resposta ou de erro do Xano; nesta mudança, a classificação de erros usa apenas o código de status HTTP.

## Decisions

### D1. Padrão Repository com interfaces assíncronas

Uma interface por agregado (`ClientRepository`, `EquipmentRepository`, `OrderRepository`) definida com `typing.Protocol`, agrupadas em um objeto `DataGateway`. Os métodos são `async`, porque os manipuladores de evento do Reflex suportam `async` e o acesso ao Xano será de rede.

- *Alternativa:* chamar `httpx` diretamente no estado. Rejeitada: acopla interface ao backend e impede testes sem rede.
- *Alternativa:* métodos síncronos. Rejeitada: bloquearia o processamento de eventos durante chamadas de rede.

### D2. Modelos com Pydantic

As entidades atuais (cliente, equipamento, ordem) passam a ser modelos Pydantic com validação dos campos obrigatórios. O estado Reflex continua expondo dicionários serializados (`model_dump`) às páginas, mantendo `rx.foreach` e o CSS atuais sem alteração nesta mudança.

- *Alternativa:* `dataclasses`. Rejeitada: Pydantic já é dependência e oferece validação e serialização prontas.

### D3. Estrutura de pacotes

```
assistencia_tech/
  config.py              # leitura das variáveis de ambiente
  models/                # modelos Pydantic das entidades
  data/
    errors.py            # hierarquia DataAccessError
    repositories.py      # Protocols e DataGateway
    factory.py           # cria o gateway conforme a configuração
    demo/                # adaptador em memória (modo demonstração)
    xano/
      client.py          # cliente HTTP (httpx.AsyncClient)
      contracts.py       # registro de contratos documentados (vazio até a documentação)
      gateway.py         # adaptador Xano das interfaces
```

Cada arquivo permanece pequeno (meta: menos de 300 linhas), bem abaixo do limite de 1000.

### D4. Configuração por variáveis de ambiente

| Variável | Uso | Padrão |
|---|---|---|
| `ASSISTENCIA_DATA_SOURCE` | `demo` ou `xano` | `demo` |
| `XANO_BASE_URL` | endereço base do API group | — (obrigatória com `xano`) |
| `XANO_TIMEOUT_SECONDS` | tempo limite das requisições | `10` |

Variáveis de autenticação **não** são definidas agora, porque dependem do contrato oficial. `.env.example` lista somente as variáveis acima. O carregamento lê `os.environ`; o uso de um arquivo `.env` local será decidido junto com a autenticação.

### D5. Registro explícito de contratos

`xano/contracts.py` mantém um dicionário de operações internas (ex.: `clients.list`) para a descrição do endpoint (método, caminho, origem na documentação). Ele começa **vazio**. O adaptador Xano consulta o registro antes de cada operação e lança `ContractPendingError` se não houver entrada, atendendo ao requisito "Somente contratos documentados" sem enviar requisições.

### D6. Hierarquia de erros e tradução para o usuário

`DataAccessError` com subclasses `ConfigurationError`, `ValidationError`, `UnauthorizedError`, `NotFoundError`, `ServiceUnavailableError`, `ContractPendingError` e `UnexpectedError`. Mapeamento HTTP: 400/422 → validação; 401/403 → não autorizado; 404 → não encontrado; 408, 429, 5xx, timeout e falha de conexão → indisponível; demais → inesperado. Cada erro carrega uma `user_message` em português; detalhes técnicos ficam apenas em log.

### D7. Estado Reflex como orquestrador

O `AppState` obtém o gateway por meio de `factory.get_gateway()` (instância por processo), carrega listas em `on_load` das páginas administrativas e mantém `is_loading`, `feedback_message` e `feedback_kind` (`success`/`error`). Mensagens são exibidas também com `rx.toast`. Os botões de envio usam `loading=` e `disabled=` vinculados a `is_loading`.

### D8. Geração de códigos de OS

A geração do código fica no adaptador de demonstração (no Xano, a origem do código dependerá do contrato). Formato `OS-{ano}-{n:05d}`, com o próximo número calculado a partir do maior código existente do ano.

### D9. Testes

`pytest` com o plugin do `anyio` (já instalado com o `httpx`) para testes assíncronos. O cliente Xano é testado com `httpx.MockTransport`, sem bibliotecas adicionais e sem rede. Um conjunto de testes de contrato interno roda contra qualquer implementação de `DataGateway`.

## Risks / Trade-offs

- [Estado Reflex compartilhado por processo no modo demonstração] → os dados de demonstração ficam em um gateway por processo; aceitável para a apresentação e documentado como limitação.
- [Contratos do Xano podem divergir dos modelos atuais] → os modelos são internos; o adaptador Xano fará o mapeamento de campos, isolando as páginas.
- [Classificação de erros só pelo status HTTP] → suficiente até conhecermos o formato de erro do Xano; refinado quando a documentação chegar.
- [Python 3.14 é recente para o ecossistema] → a `.venv` atual já executa Reflex 0.8.28; qualquer incompatibilidade será registrada antes de mudar versões.

## Migration Plan

1. Introduzir a camada de dados e o modo demonstração com os mesmos dados atuais.
2. Migrar o `AppState` para o gateway, sem alterar rotas nem CSS.
3. Validar no navegador todos os fluxos atuais (consulta de OS, cadastros, busca, status).
4. Rollback: reverter o commit da migração do estado; as páginas não mudam de contrato.

## Open Questions

- Quais API groups, endpoints, formatos de resposta e fluxo de autenticação o workspace Xano expõe? (bloqueia o grupo de tarefas 6; não altera a arquitetura acima)
