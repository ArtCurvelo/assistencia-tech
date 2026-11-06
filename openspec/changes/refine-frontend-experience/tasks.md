# Tasks

## 1. Contenção e grade responsiva

- [ ] 1.1 Conter painéis e tabelas na largura da coluna (CSS); verificar no navegador em 375 px que `/admin/clientes`, `/admin/clientes/4`, `/admin/equipamentos`, `/admin/ordens` e `/admin/ordens/OS-2026-00125` têm largura de página igual à da tela.
- [ ] 1.2 Tornar a grade de indicadores adaptável (2/4 colunas) com valores sem quebra; verificar no navegador em 375 px e 1366 px.

## 2. Navegação

- [ ] 2.1 Implementar o menu administrativo recolhível abaixo de 900 px, com `aria-expanded` e fechamento ao escolher uma página; verificar no navegador em 375 px, 768 px e 1366 px.
- [ ] 2.2 Manter "Entrar" visível para visitantes no cabeçalho público do celular; verificar no navegador em 375 px.
- [ ] 2.3 Adicionar o link "Pular para o conteúdo" e o foco visível; verificar com Tab no navegador.

## 3. Painel

- [ ] 3.1 Criar `payment_summary` e adicionar cores e quantidades numéricas a `status_counts`, com testes em `tests/test_presenters.py`; verificar com `pytest`.
- [ ] 3.2 Substituir as barras do painel por gráficos Recharts (status e pagamentos); verificar no navegador que todos os status e situações aparecem com quantidades.
- [ ] 3.3 Exibir "—" nos indicadores quando o carregamento falhar; verificar no navegador no modo Xano sem contratos.

## 4. Formulários e páginas

- [ ] 4.1 Preservar os dados de formulários recusados e limpar após o sucesso (clientes, equipamentos, abertura de OS, itens e pagamentos); verificar no navegador com um cadastro recusado e outro aceito.
- [ ] 4.2 Criar a página "Página não encontrada"; verificar no navegador com uma rota inexistente.

## 5. Verificação integrada

- [ ] 5.1 Executar `pytest`, `openspec validate --all --strict` e a contagem de linhas, e registrar os resultados neste arquivo.
- [ ] 5.2 Percorrer as páginas públicas, administrativas e do portal em 375 px, 768 px e 1366 px, registrando a largura da página e as capturas de tela verificadas neste arquivo.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
