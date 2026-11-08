# Proposal: Avaliação do atendimento (NPS)

## Why

A assistência não sabe se o cliente ficou satisfeito: a página inicial fala em clientes satisfeitos, mas o sistema não mede isso. Sem retorno do cliente, não há como comparar técnicos, perceber queda de qualidade ou responder a uma reclamação. O NPS (Net Promoter Score) é a métrica de satisfação mais usada no mercado: uma pergunta de 0 a 10, simples para o cliente e fácil de acompanhar pela empresa.

## What Changes

- **Avaliação no portal:** depois da entrega, o cliente responde "De 0 a 10, quanto você recomendaria a Assistência TECH a um amigo ou familiar?" e pode deixar um comentário (até 500 caracteres). Cada ordem recebe uma única avaliação, que não pode ser alterada.
- **Detalhe da ordem:** a equipe vê a nota, a classificação (promotor, neutro ou detrator), o comentário e a data.
- **Relatórios:** NPS do período (percentual de promotores menos o de detratores), nota média, quantidade de respostas por grupo, nota média por técnico e os comentários mais recentes.
- **Painel:** indicador do NPS dos últimos 90 dias.
- **Backend Xano:** tabela `avaliacao`, endpoint `POST /portal/avaliacao` (somente o cliente dono da ordem entregue, uma vez) e a avaliação (`_avaliacao`) nas leituras das ordens.

## Capabilities

### New Capabilities

- `service-rating`: avaliação do atendimento pelo cliente e indicadores de NPS.

### Modified Capabilities

- Nenhuma.

## Impact

- **Código:** `models` (avaliação na ordem), `domain/rating.py`, `domain/reports.py`, `services/portal.py`, permissões, adaptadores (demonstração e Xano), presenters, portal, detalhe da ordem, painel e relatórios.
- **Backend:** tabela `avaliacao`, addon `atech_avaliacao_da_os`, endpoint `portal/avaliacao` e leituras de `os_servicos` e `portal/minhas_ordens`.
- **Testes:** domínio, serviço, permissões e adaptador Xano simulado.

## Out of Scope

- Pesquisa por e-mail ou mensagem.
- Resposta pública da assistência ao comentário.
- Moderação ou exclusão de comentários.
