# service-rating Specification

## Purpose
Define a avaliação do atendimento do Assistência TECH: a nota de 0 a 10 dada pelo cliente no portal após a entrega, uma vez por ordem, e os indicadores de satisfação (NPS) do painel e dos relatórios.

## Requirements

### Requirement: Avaliação pelo cliente

O portal SHALL permitir que o cliente avalie cada ordem própria com status Entregue respondendo, com uma nota inteira de 0 a 10, quanto recomendaria a assistência, e deixando um comentário opcional de até 500 caracteres. Cada ordem MUST aceitar uma única avaliação, que não pode ser alterada. Ordens em outros status, ordens de outros clientes e usuários sem o perfil Cliente MUST ter a avaliação recusada.

#### Scenario: Avaliação de ordem entregue
- **WHEN** a cliente avalia a própria ordem entregue com nota 9 e o comentário "Rápido e caprichado"
- **THEN** a avaliação é registrada e o portal passa a exibir "Sua avaliação: 9" com o comentário, sem o formulário

#### Scenario: Segunda avaliação
- **WHEN** a cliente tenta avaliar de novo uma ordem já avaliada
- **THEN** a avaliação é recusada com a mensagem "Esta ordem já foi avaliada."

#### Scenario: Ordem ainda em reparo
- **WHEN** a cliente tenta avaliar uma ordem Em reparo
- **THEN** a avaliação é recusada com a mensagem "Só ordens entregues podem ser avaliadas."

#### Scenario: Nota fora da escala
- **WHEN** a nota enviada é 11
- **THEN** a avaliação é recusada com a mensagem "A nota deve ser um número inteiro de 0 a 10."

### Requirement: Avaliação na ordem de serviço

O detalhe da ordem SHALL exibir à equipe a nota, a classificação (Promotor para 9 e 10, Neutro para 7 e 8, Detrator para 0 a 6), o comentário e a data da avaliação.

#### Scenario: Ordem avaliada com nota 6
- **WHEN** a atendente abre uma ordem avaliada com nota 6
- **THEN** o detalhe exibe a nota 6 com a classificação "Detrator" e o comentário

### Requirement: Indicadores de satisfação

Os relatórios SHALL exibir, para as avaliações feitas no período, o NPS (percentual de promotores menos o de detratores, arredondado), a nota média, a quantidade de promotores, neutros e detratores, a nota média por técnico e os comentários mais recentes com o código da ordem, a nota e a data, sem o nome do cliente. O painel SHALL exibir o NPS dos últimos 90 dias. Sem avaliações, os indicadores MUST exibir "—".

#### Scenario: Cálculo do NPS
- **WHEN** o período tem 5 avaliações: notas 10, 9, 8, 6 e 3
- **THEN** o relatório exibe NPS 0 (40% de promotores − 40% de detratores), nota média 7,2 e 2 promotores, 1 neutro e 2 detratores

#### Scenario: Período sem avaliações
- **WHEN** nenhuma avaliação foi feita no período
- **THEN** o NPS e a nota média aparecem como "—"
