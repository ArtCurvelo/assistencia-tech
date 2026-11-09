# Design: Página de serviços e painel administrativo

## Decisions

### D1. Conteúdo público sem dados inventados

A página de serviços descreve só o que o sistema faz de verdade: previsão padrão de 7 dias, orçamento aprovado ou recusado pelo cliente no portal, devolução das peças e cancelamento na recusa, consulta pelo código ou QR code, garantia de 90 dias após a entrega (CDC, art. 26, II) e avaliação de 0 a 10. Preços e prazos de serviços específicos ficam de fora, porque não existem no sistema.

### D2. "Precisa de atenção" calculado das ordens já carregadas

O painel já carrega todas as ordens. Uma função pura (`attention_rows`) separa, em ordem de prioridade:
1. **Atrasada** — antes de Concluído e com a previsão vencida (mais dias de atraso primeiro);
2. **Pronta para entrega** — status Concluído;
3. **Aguardando o cliente** — status Aguardando aprovação (mais antigas primeiro).

Cada ordem aparece uma vez (a primeira regra que a pega) e a lista mostra até 8, com o total. Sem nenhuma, o painel diz "Tudo em dia".

### D3. Visão do técnico

Para o perfil Técnico, "Meus atendimentos" lista as ordens em aberto (de Recebido a Em reparo) atribuídas a ele, mais antigas primeiro. Os demais perfis não veem esse quadro.

### D4. Atalhos por permissão

Os atalhos usam as permissões já calculadas na sessão (`user_permissions`): "Nova ordem" (`orders.open`), "Novo cliente" (`clients.manage`), "Estoque" (`stock.view`) e "Relatórios" (`reports.view`). Quem não tem a permissão não vê o atalho; a página de destino continua verificando o acesso.

### D5. Recebido no mês

Soma dos pagamentos cuja data cai no mês corrente (horário de Brasília), de todas as ordens.

## Risks / Trade-offs

- [Equipe acessava o painel pelo botão da página inicial] → o "Entrar" do cabeçalho leva ao login, que encaminha cada perfil à sua área.
