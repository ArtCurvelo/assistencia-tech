# Modelo de dados

Modelo de domínio do Assistência TECH, definido em `assistencia_tech/models/entities.py` e especificado pelas capacidades `client-management`, `equipment-management` e `service-orders` (mudança `expand-service-domain`).

> O modelo é **interno** à aplicação. A estrutura das tabelas no Xano será mapeada para ele somente quando a documentação oficial da API for fornecida (ver `XANO_INTEGRATION.md`).

## Diagrama entidade-relacionamento

```mermaid
erDiagram
    CLIENTE ||--o{ EQUIPAMENTO : possui
    CLIENTE ||--o{ ORDEM_DE_SERVICO : solicita
    EQUIPAMENTO ||--o{ ORDEM_DE_SERVICO : "é atendido em"
    TECNICO |o--o{ ORDEM_DE_SERVICO : "é responsável por"
    ORDEM_DE_SERVICO ||--o{ ITEM_DE_ORCAMENTO : contém
    ORDEM_DE_SERVICO ||--o{ PAGAMENTO : recebe
    ORDEM_DE_SERVICO ||--|{ EVENTO_DE_HISTORICO : registra

    CLIENTE {
        string id PK
        string nome
        string cpf UK "11 dígitos, validado"
        string email UK
        string telefone "10 ou 11 dígitos com DDD"
    }
    EQUIPAMENTO {
        string id PK
        string cliente_id FK
        string tipo "Computador, Notebook, Console, Celular, Tablet, Outro"
        string marca
        string modelo
        string numero_serie UK "opcional"
        string observacoes
    }
    TECNICO {
        string id PK
        string nome
        string especialidade
    }
    ORDEM_DE_SERVICO {
        string codigo PK "OS-AAAA-NNNNN"
        string cliente_id FK
        string equipamento_id FK
        string tecnico_id FK "opcional"
        string problema_relatado
        string status
        string diagnostico
        string motivo_cancelamento
        datetime aberta_em
        datetime atualizada_em
    }
    ITEM_DE_ORCAMENTO {
        string id PK
        string tipo "Serviço ou Peça"
        string descricao
        int quantidade "serviços = 1"
        decimal valor_unitario "> 0, 2 casas"
    }
    PAGAMENTO {
        string id PK
        decimal valor "> 0, até o saldo"
        string forma "Dinheiro, PIX, Débito, Crédito"
        datetime pago_em
    }
    EVENTO_DE_HISTORICO {
        datetime em
        string autor
        string tipo
        string descricao
    }
```

### Regras de integridade

| Regra | Onde é garantida |
|---|---|
| CPF válido e único; e-mail único | `ClientCreate` (formato) e `services/clients.py` (unicidade) |
| Cliente com equipamentos ou ordens não pode ser excluído | `ClientService.delete` |
| Número de série único quando informado | `EquipmentService` |
| Equipamento com ordens não troca de cliente nem é excluído | `EquipmentService.update` / `delete` |
| Equipamento da OS pertence ao cliente da OS | `OrderService.open` |
| Itens, pagamentos e histórico pertencem à OS (agregado) | `ServiceOrder` (tuplas imutáveis) |
| Histórico só recebe novos eventos | `domain/history.py` (`append`) |

## Ciclo de vida da ordem de serviço

```mermaid
stateDiagram-v2
    [*] --> Recebido
    Recebido --> EmAnalise: técnico atribuído
    EmAnalise --> AguardandoAprovacao: diagnóstico e ≥ 1 item
    AguardandoAprovacao --> EmReparo: orçamento aprovado
    EmReparo --> Concluido
    Concluido --> Entregue: saldo devedor = 0
    Recebido --> Cancelado: motivo
    EmAnalise --> Cancelado: motivo
    AguardandoAprovacao --> Cancelado: motivo
    EmReparo --> Cancelado: motivo
    Cancelado --> Entregue: devolução do equipamento
    Entregue --> [*]

    EmAnalise: Em análise
    AguardandoAprovacao: Aguardando aprovação
    EmReparo: Em reparo
    Concluido: Concluído
```

- Diagnóstico e orçamento podem ser alterados em **Em análise**, **Aguardando aprovação** e **Em reparo**.
- O técnico pode ser trocado enquanto a ordem não estiver **Entregue** ou **Cancelada**.
- Pagamentos são aceitos em ordens não canceladas, até o saldo devedor.
- A tabela de transições está em `domain/order_workflow.py` (`TRANSITIONS`) e é coberta por `tests/test_order_rules.py`.

## Valores

`total = Σ serviços + Σ (quantidade × valor unitário das peças)`; `saldo = total − Σ pagamentos`. A situação do pagamento é **Pendente** (nada pago), **Parcial** ou **Pago**. Ordens canceladas sem pagamento aparecem como **Não se aplica**. Valores usam `Decimal` arredondado em centavos e são exibidos como `R$ 1.234,56`.
