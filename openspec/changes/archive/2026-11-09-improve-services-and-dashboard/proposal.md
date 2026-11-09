# Proposal: Página de serviços completa e painel administrativo orientado a ações

## Why

- A página inicial mostra a visitantes um botão "Área administrativa", que só interessa à equipe e leva a uma tela de login para quem não é colaborador.
- A página de serviços só lista categorias: não explica como o atendimento funciona, quais são as garantias nem responde às dúvidas mais comuns, embora o sistema já ofereça tudo isso (previsão de entrega, aprovação do orçamento pelo portal, consulta por QR code, garantia de 90 dias, avaliação).
- O painel administrativo mostra números e gráficos, mas não diz o que fazer agora: as ordens atrasadas, as que esperam o cliente e as prontas para entrega ficam escondidas na lista geral, e o técnico não vê de imediato os próprios atendimentos.

## What Changes

- **Página inicial:** sai o botão "Área administrativa"; a equipe entra pelo "Entrar" do cabeçalho.
- **Página de serviços:** além do catálogo, "Como funciona o atendimento" (seis etapas, da entrada à garantia), "Nossos compromissos" (previsão de entrega, nada sem aprovação, acompanhamento online, garantia de 90 dias), perguntas frequentes e chamadas para consultar uma ordem ou criar conta. Todo o texto descreve regras que o sistema já aplica, sem preços ou números inventados.
- **Painel administrativo:**
  - saudação com o nome, o perfil e a data;
  - atalhos para as ações permitidas ao perfil (nova ordem, novo cliente, estoque, relatórios);
  - "Precisa de atenção": ordens atrasadas, aguardando aprovação e prontas para entrega, em ordem de prioridade, com link para cada ordem;
  - "Meus atendimentos" para o técnico: as ordens em aberto atribuídas a ele;
  - indicador "Recebido no mês" (pagamentos do mês corrente).

## Capabilities

### New Capabilities

- `public-site`: página inicial e página de serviços.
- `admin-dashboard`: painel administrativo.

### Modified Capabilities

- Nenhuma.

## Impact

- **Código:** `pages/public.py`, `pages/dashboard.py`, `presenters.py`, `state/base.py` (dados do painel), CSS.
- **Backend:** nenhuma mudança; o painel usa as leituras já carregadas.
- **Testes:** presenters do painel (prioridade, limites, técnico, recebido no mês).

## Out of Scope

- Tabela de preços dos serviços.
- Personalização do painel pelo usuário.
