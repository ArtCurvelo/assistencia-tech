# Spec Delta

## ADDED Requirements

### Requirement: Prazos e garantia no portal

O portal SHALL exibir a previsão de entrega das ordens do cliente e, nas ordens entregues com garantia, a data "Garantia até". Uma ordem em garantia SHALL ser identificada como tal, sem valor a pagar.

#### Scenario: Ordem em andamento
- **WHEN** o cliente abre uma ordem Em reparo com previsão para 20/11/2026
- **THEN** o portal exibe "Previsão de entrega: 20/11/2026"

#### Scenario: Ordem entregue com garantia
- **WHEN** o cliente abre uma ordem entregue em 07/11/2026
- **THEN** o portal exibe "Garantia até 05/02/2027"
