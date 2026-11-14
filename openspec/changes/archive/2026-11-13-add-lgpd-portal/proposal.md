# Proposal: Direitos do titular (LGPD) no portal do cliente

## Why

O sistema guarda dados pessoais (nome, CPF, e-mail, telefone) e a Lei Geral de Proteção de Dados (Lei 13.709/2018, art. 18) garante ao titular o acesso aos próprios dados, a portabilidade e a eliminação dos dados tratados com o seu consentimento. Hoje o cliente não tem como baixar o que o sistema sabe sobre ele nem pedir a exclusão da conta, e a assistência não teria um procedimento para atender o pedido.

## What Changes

- **Baixar meus dados:** no portal, o cliente baixa um arquivo JSON com o cadastro, os equipamentos, as ordens (itens, pagamentos, andamento) e as avaliações dele.
- **Excluir minha conta:** o cliente confirma com a senha e, se não houver ordem em andamento, o sistema:
  - substitui nome, CPF, e-mail e telefone por marcadores e marca o cadastro como anonimizado;
  - desativa o login;
  - apaga os comentários das avaliações (as notas continuam, sem identificação);
  - **mantém** as ordens e os valores, que a assistência deve guardar por obrigação legal e fiscal (LGPD, art. 16, I).
- A equipe passa a ver o cadastro como "Cliente anonimizado", sem dados pessoais.
- **Xano:** campo `anonimizado` na tabela `cliente` e endpoint `POST /portal/excluir_conta`.

## Capabilities

### New Capabilities

- `privacy`: exportação e exclusão de dados pelo titular.

### Modified Capabilities

- Nenhuma.

## Impact

- **Backend:** tabela `cliente` (novo campo) e novo endpoint no grupo `assistencia-tech-os`.
- **Código:** modelo `Client`, mapeador, repositórios (demonstração e Xano), `PortalService`, portal.
- **Testes:** exportação, exclusão, recusas (senha errada, ordem em andamento), leitura de cliente anonimizado e adaptador simulado.

## Out of Scope

- Exclusão pedida pela equipe em nome do cliente.
- Prazos automáticos de descarte de dados antigos.
