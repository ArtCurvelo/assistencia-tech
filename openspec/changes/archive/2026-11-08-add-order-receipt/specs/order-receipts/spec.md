# Spec Delta

## ADDED Requirements

### Requirement: Comprovante de entrada

O sistema SHALL gerar, para qualquer ordem de serviço, um comprovante de entrada com os dados da assistência, o código da ordem, a data de abertura, o nome, o CPF mascarado e o telefone do cliente, o equipamento com número de série, o problema relatado, a previsão de entrega, o status atual e espaço para as assinaturas do cliente e da assistência. O comprovante MUST NOT exibir o CPF completo.

#### Scenario: Ordem em reparo
- **WHEN** a atendente abre o comprovante de uma ordem Em reparo
- **THEN** o documento se chama "Comprovante de entrada" e mostra o código, o cliente com CPF no formato `***.***.***-NN`, o equipamento, o problema relatado e a previsão de entrega

#### Scenario: Ordem cancelada
- **WHEN** o comprovante de uma ordem cancelada é aberto
- **THEN** o comprovante de entrada mostra o status Cancelado e o motivo do cancelamento

### Requirement: Comprovante de entrega

Para ordens entregues, o sistema SHALL gerar um comprovante de entrega com o conteúdo do comprovante de entrada mais os serviços e peças, os totais, os pagamentos, a data da entrega e, se houver garantia, a data "Garantia até".

#### Scenario: Ordem entregue após conclusão
- **WHEN** o comprovante de uma ordem concluída e entregue em 07/11/2026 é aberto
- **THEN** o documento se chama "Comprovante de entrega" e mostra os itens, o total pago, a data da entrega e "Garantia até 05/02/2027"

### Requirement: QR code da consulta

Todo comprovante SHALL trazer um QR code com o endereço da consulta pública da ordem (`<endereço público>/consulta/<código>`), gerado pelo próprio sistema, e o mesmo endereço por extenso. O endereço público SHALL vir de `ASSISTENCIA_PUBLIC_URL` quando configurado e, sem ele, do endereço pelo qual o sistema foi acessado.

#### Scenario: Endereço configurado
- **WHEN** `ASSISTENCIA_PUBLIC_URL` é `https://assistencia.exemplo.com.br` e o comprovante da OS-2026-00125 é aberto
- **THEN** o QR code e o texto abaixo dele apontam para `https://assistencia.exemplo.com.br/consulta/OS-2026-00125`

### Requirement: Impressão e PDF

O comprovante SHALL ter o botão "Imprimir / salvar PDF" e uma versão de impressão sem menus nem botões, com fundo claro, no tamanho A4.

#### Scenario: Impressão
- **WHEN** o usuário aciona "Imprimir / salvar PDF"
- **THEN** o navegador abre a impressão, na qual só aparece o comprovante

### Requirement: Acesso aos comprovantes

Colaboradores com permissão de consultar ordens SHALL acessar o comprovante de qualquer ordem a partir do detalhe. Clientes SHALL acessar pelo portal somente o comprovante das próprias ordens; ordens de outros clientes MUST ser tratadas como não encontradas. Visitantes sem sessão MUST ser enviados ao login.

#### Scenario: Cliente tenta o comprovante de outra pessoa
- **WHEN** um cliente acessa `/minha-conta/ordens/<código de outro cliente>/comprovante`
- **THEN** a página informa que a ordem não foi encontrada, sem exibir nenhum dado dela

#### Scenario: Visitante sem sessão
- **WHEN** um visitante sem sessão acessa `/admin/ordens/OS-2026-00125/comprovante`
- **THEN** é enviado à página de login
