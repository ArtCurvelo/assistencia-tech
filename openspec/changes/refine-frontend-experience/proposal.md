# Proposal: Refinamento do frontend e responsividade

## Why

A auditoria da interface (2026-11-06, larguras de 1366 px e 375 px) mostrou que a aplicação ainda não atende plenamente às especificações `responsive-interface` e `design-system`:

- No celular, as páginas de clientes, detalhe do cliente, equipamentos, ordens e detalhe da OS ficam mais largas que a tela (de 545 a 754 px em 375 px), o que provoca rolagem horizontal da página inteira.
- No celular, a barra lateral administrativa ocupa a primeira tela inteira antes do conteúdo.
- Os indicadores do painel ficam em 4 colunas no celular, a ponto de quebrar o valor "R$ 706,00".
- O gráfico "Ordens por status" usa cores translúcidas e as barras ficam quase invisíveis.
- No celular, o menu público esconde o botão "Entrar" de visitantes.
- Formulários são limpos mesmo quando a operação é recusada, e o usuário perde o que digitou.
- No modo Xano, os cartões do painel ficam sem valores.

A apresentação acadêmica depende de uma interface consistente em qualquer tamanho de tela.

## What Changes

- Navegação administrativa recolhível no celular (barra superior com botão de menu), mantendo a barra lateral no computador.
- Contenção de tabelas e painéis: a rolagem horizontal fica restrita à tabela, nunca à página.
- Indicadores do painel com grade adaptável (2 colunas no celular, 4 no computador) e valores sem quebra.
- Painel com gráficos legíveis: distribuição das ordens por status e situação dos pagamentos, com cores sólidas e rótulos.
- Formulários que preservam os dados digitados quando a operação é recusada e são limpos apenas após o sucesso.
- Indicadores com "—" e explicação quando os dados não puderem ser carregados.
- Botão "Entrar" visível para visitantes no celular.
- Acessibilidade de teclado: link "Pular para o conteúdo", foco visível em links, botões e campos, e rótulos acessíveis nos botões de ícone.
- Página "Página não encontrada" para rotas inexistentes, com retorno à área do usuário.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `responsive-interface`: novos requisitos de navegação administrativa recolhível, contenção de tabelas e grade adaptável de indicadores.
- `design-system`: novos requisitos de preservação de formulários, gráficos do painel, indisponibilidade de indicadores, navegação por teclado e página não encontrada.

## Impact

- **Código:** `components/layout.py` (menu móvel, link de salto), `components/ui.py`, `pages/dashboard.py` (gráficos com `rx.recharts`), formulários de clientes, equipamentos, ordens e detalhe da OS (chave de formulário), página 404, `assets/style.css`.
- **Estado:** controle do menu móvel e chaves de formulário; nenhuma mudança em serviços ou regras de negócio.
- **Testes:** dados dos gráficos nos apresentadores; verificação no navegador em 375 px, 768 px e 1366 px.

## Out of Scope

- Mudanças de regras de negócio, permissões ou integração com o Xano.
- Tema claro e internacionalização.
- Relatórios administrativos e exportação (mudança de administração).
