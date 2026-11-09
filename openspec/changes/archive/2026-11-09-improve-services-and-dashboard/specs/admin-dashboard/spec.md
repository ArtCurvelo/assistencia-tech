# Spec Delta

## ADDED Requirements

### Requirement: Saudação e atalhos

O painel SHALL saudar o colaborador pelo nome, com o perfil e a data de hoje, e SHALL oferecer atalhos apenas para as ações permitidas ao perfil: nova ordem, novo cliente, estoque e relatórios.

#### Scenario: Técnico no painel
- **WHEN** um técnico abre o painel
- **THEN** vê a saudação com o próprio nome e não vê os atalhos "Nova ordem", "Novo cliente" e "Relatórios"

### Requirement: Ordens que precisam de atenção

O painel SHALL listar, em ordem de prioridade, as ordens atrasadas (mais dias de atraso primeiro), as prontas para entrega (status Concluído) e as aguardando aprovação do cliente (mais antigas primeiro), cada ordem uma única vez, até 8 itens, com o total e link para cada ordem. Sem nenhuma, SHALL exibir "Tudo em dia".

#### Scenario: Ordem atrasada e aguardando aprovação
- **WHEN** existe uma ordem Em reparo atrasada há 3 dias e outra Aguardando aprovação
- **THEN** a atrasada aparece primeiro com "Atrasada há 3 dias" e a outra em seguida com "Aguardando o cliente"

#### Scenario: Nada pendente
- **WHEN** nenhuma ordem está atrasada, concluída ou aguardando aprovação
- **THEN** o quadro exibe "Tudo em dia"

### Requirement: Atendimentos do técnico

Para o perfil Técnico, o painel SHALL listar as ordens em aberto atribuídas a ele, das mais antigas para as mais novas.

#### Scenario: Técnico com ordens
- **WHEN** o técnico Carlos tem uma ordem Em reparo e outra Aguardando aprovação
- **THEN** "Meus atendimentos" mostra as duas, a mais antiga primeiro

### Requirement: Recebido no mês

O painel SHALL exibir a soma dos pagamentos registrados no mês corrente.

#### Scenario: Pagamentos de meses diferentes
- **WHEN** há um pagamento de R$ 100,00 neste mês e outro de R$ 50,00 no mês anterior
- **THEN** "Recebido no mês" mostra R$ 100,00
