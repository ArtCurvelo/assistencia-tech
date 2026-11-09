# Spec Delta

## ADDED Requirements

### Requirement: Números reais na página inicial

A página inicial SHALL exibir indicadores calculados a partir dos dados do sistema: equipamentos entregues, ordens em atendimento, a satisfação dos clientes em NPS com a quantidade de avaliações e a garantia de 90 dias. Os indicadores MUST NOT expor dados pessoais, valores ou códigos de ordens, e MUST exibir "—" quando os dados não estiverem disponíveis, nunca números fictícios.

#### Scenario: Visitante vê os números do sistema
- **WHEN** o sistema tem 3 ordens entregues, 2 em atendimento e avaliações 10, 9 e 5
- **THEN** a página inicial mostra 3 equipamentos entregues, 2 em atendimento e NPS +33 com 3 avaliações

#### Scenario: Backend indisponível
- **WHEN** o backend não responde ao carregar a página inicial
- **THEN** os indicadores de entregas, atendimentos e NPS mostram "—" e o restante da página funciona

#### Scenario: Muitas visitas seguidas
- **WHEN** a página inicial é aberta várias vezes em menos de 5 minutos
- **THEN** o backend é consultado uma única vez nesse intervalo
