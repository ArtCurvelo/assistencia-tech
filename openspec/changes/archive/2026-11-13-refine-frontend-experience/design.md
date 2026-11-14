# Design: Refinamento do frontend e responsividade

## Context

Motivação e diagnóstico em `proposal.md`; comportamento em `specs/responsive-interface` e `specs/design-system`.

Causa medida da largura excedente no celular: os conteúdos administrativos são `rx.vstack` (flex em coluna com `align-items: start`), então cada painel assume a largura do próprio conteúdo (por exemplo, 536 px para a tabela do orçamento) em vez de se limitar à coluna. O `.table-wrap` com `overflow-x: auto` não chega a atuar, porque o pai já cresceu.

## Decisions

### D1. Contenção por CSS

`.panel-card`, `.table-wrap` e os filhos diretos de `.admin-content` recebem `width: 100%`, `max-width: 100%` e `min-width: 0`. Com isso, o `overflow-x: auto` passa a funcionar dentro do painel. Não é preciso mudar a estrutura dos componentes.

### D2. Menu móvel com estado e CSS

`AppState.mobile_menu_open` controla a classe `sidebar-open`. Abaixo de 900 px, `.admin-layout` passa a ter uma coluna, e `.sidebar` vira uma barra superior com a marca e o botão de menu (`aria-expanded`, `aria-controls`). A navegação e o bloco do usuário só aparecem quando o menu está aberto. Os links do menu disparam `close_mobile_menu`. Acima de 900 px o botão fica oculto e o layout lateral continua igual.

- *Alternativa:* `rx.drawer`. Rejeitada para manter um único markup de navegação (sem duplicar links) e o comportamento atual do computador.

### D3. Formulários com chave de versão

Cada formulário de cadastro recebe `key=State.<form>_key`, com `reset_on_submit=False`. Depois do sucesso, o manipulador incrementa a chave e o React remonta o formulário vazio, o que também restaura os selects do Radix. Em caso de erro, a chave não muda e os valores permanecem.

- *Alternativa:* `reset_on_submit=True` (comportamento atual, que perde os dados ao recusar) ou um script `form.reset()` (não restaura a exibição dos selects do Radix).

### D4. Gráficos com `rx.recharts`

O Recharts já vem com o Reflex 0.8. O painel usa um `bar_chart` horizontal de ordens por status (cor sólida por status) e um `pie_chart` de situação dos pagamentos (Pendente, Parcial, Pago, considerando as ordens não canceladas com valor). Os dados vêm prontos dos apresentadores (`status_counts`, `payment_summary`), com cor e quantidade numérica. A paleta é derivada das cores de status já usadas nos badges, em versão opaca.

### D5. Indicadores indisponíveis

`dashboard_metrics` ganha um valor padrão `EMPTY_METRICS` com "—", atribuído quando o carregamento falha.

### D6. Acessibilidade

O link de salto (`.skip-link`) fica visualmente oculto até receber foco e aponta para `#conteudo`, `id` do conteúdo principal. Regras `:focus-visible` com contorno verde valem para links, botões, campos e gatilhos de select.

### D7. Página 404

O Reflex 0.8 trata a rota especial `constants.Page404.SLUG` como página de rota inexistente (`App.add_page`, verificado em `reflex/app.py`). A página personalizada é registrada nessa rota e usa `AppState.load_session` para oferecer o link à área do usuário.

## Risks / Trade-offs

- [Recharts aumenta o pacote do frontend] → já é dependência do Reflex; o uso fica restrito ao painel.
- [Mudança de chave remonta o formulário] → efeito desejado; só acontece após o sucesso.

## Migration Plan

Mudanças apenas de apresentação; o rollback é reverter o commit.
