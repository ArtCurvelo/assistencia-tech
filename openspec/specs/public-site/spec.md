# public-site Specification

## Purpose
Define o site público do Assistência TECH: a página inicial voltada a clientes e a página de serviços com etapas do atendimento, compromissos e perguntas frequentes.

## Requirements

### Requirement: Página inicial para clientes

A página inicial SHALL ser voltada a clientes e visitantes, com apresentação dos serviços, consulta pública da ordem e acesso a entrar ou criar conta pelo cabeçalho. Ela MUST NOT exibir atalhos para a área administrativa.

#### Scenario: Visitante na página inicial
- **WHEN** um visitante abre a página inicial
- **THEN** vê "Conhecer serviços" e não vê o botão "Área administrativa"

### Requirement: Página de serviços completa

A página de serviços SHALL apresentar o catálogo de serviços, as etapas do atendimento (entrada, diagnóstico, orçamento, reparo, entrega e garantia), os compromissos da assistência, perguntas frequentes e chamadas para consultar uma ordem e criar conta. O conteúdo MUST descrever apenas regras aplicadas pelo sistema, sem preços ou estatísticas que o sistema não registra.

#### Scenario: Cliente quer saber como funciona
- **WHEN** um visitante abre a página de serviços
- **THEN** vê as seis etapas do atendimento, a garantia de 90 dias e que nenhum reparo começa sem a aprovação do orçamento

#### Scenario: Dúvida frequente
- **WHEN** o visitante abre a pergunta "E se eu recusar o orçamento?"
- **THEN** a resposta explica que a ordem é cancelada sem cobrança do reparo e o equipamento fica disponível para retirada

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
