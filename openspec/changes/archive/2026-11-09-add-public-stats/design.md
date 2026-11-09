# Design: Números reais na página inicial

## Decisions

### D1. Só contagens no endpoint público

`GET /estatisticas_publicas` (sem autenticação) devolve `entregues`, `em_atendimento`, `avaliacoes`, `promotores` (nota ≥ 9) e `detratores` (nota ≤ 6). São cinco números agregados: nenhum nome, código, valor ou comentário. O NPS é calculado na aplicação com `domain.rating`, a mesma regra dos relatórios.

### D2. Cache de 5 minutos no servidor da aplicação

A página inicial é pública e pode receber muitas visitas; o Xano gratuito aceita 10 requisições a cada 20 segundos, compartilhadas com o sistema todo. O serviço guarda os números por 5 minutos (por processo). Números de até 5 minutos atrás são aceitáveis para uma vitrine.

### D3. Sem números inventados em falha

Se o backend estiver indisponível, os cartões mostram "—" e a página continua funcionando. Nunca há valor padrão fictício.

### D4. Contrato

Como a resposta é um objeto montado no XanoScript (não um registro de tabela), a documentação gerada pelo Xano pode não detalhar os campos; o contrato-alvo registra o endpoint e as entradas, e os campos são conferidos pela chamada real no roteiro de verificação e pelo teste do adaptador.

## Risks / Trade-offs

- [Números com até 5 minutos de atraso] → aceitável para a página inicial; os relatórios internos continuam em tempo real.
