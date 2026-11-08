# Design: Avaliação do atendimento (NPS)

## Decisions

### D1. Escala e classificação do NPS

Nota inteira de 0 a 10. Promotores: 9 e 10; neutros: 7 e 8; detratores: 0 a 6. NPS = percentual de promotores − percentual de detratores, arredondado para inteiro (de −100 a 100). Sem respostas, o NPS é "—". As funções puras ficam em `domain/rating.py`.

### D2. Uma avaliação por ordem, imutável

Só a ordem **Entregue** do próprio cliente pode ser avaliada, uma única vez; a avaliação não é editada nem excluída, para que o indicador não seja manipulado. Comentário opcional, com espaços removidos e até 500 caracteres. A permissão nova `portal.rate_service` é exclusiva do perfil Cliente (como `portal.decide_budget`).

### D3. A avaliação faz parte da leitura da ordem

`ServiceOrder.rating` (nota, comentário, data) vem junto com a ordem: no Xano, pelo addon `_avaliacao` nas leituras de `os_servicos` e `portal/minhas_ordens`. Os relatórios e o painel já carregam as ordens, então o NPS não exige leitura nova.

### D4. Período dos indicadores

Nos relatórios, entram as avaliações **feitas** dentro do período escolhido (pela data da avaliação). O painel mostra os últimos 90 dias. A nota média por técnico usa as avaliações do período das ordens daquele técnico.

### D5. Xano

Tabela `avaliacao` (`os_servicos_id` com índice único, `cliente_id`, `nota`, `comentario`). `POST /portal/avaliacao` valida o perfil cliente, a posse da ordem, o status `entregue`, a nota de 0 a 10, o tamanho do comentário e a ausência de avaliação anterior; o índice único também impede duas avaliações em requisições simultâneas.

### D6. Privacidade

Os relatórios mostram os comentários com o código da ordem, a nota e a data, sem nome do cliente; quem precisar do contexto abre a ordem (o acesso à ordem já é controlado). O portal mostra ao cliente apenas a avaliação das próprias ordens.

## Risks / Trade-offs

- [Poucas respostas tornam o NPS instável] → o relatório mostra a quantidade de respostas ao lado do NPS.
- [Cliente insatisfeito não pode corrigir a nota] → escolha deliberada (D2); o comentário registra o contexto.
