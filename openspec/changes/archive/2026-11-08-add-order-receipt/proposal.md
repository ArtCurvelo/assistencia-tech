# Proposal: Comprovante da ordem com QR code

## Why

Hoje o cliente deixa o equipamento na assistência e sai sem nenhum documento: não leva o código da ordem, a previsão de entrega nem o que foi combinado. Na retirada, também não recebe nada que registre o serviço feito, o valor pago e até quando vale a garantia de 90 dias. Um comprovante impresso (ou salvo em PDF) é o documento que uma assistência técnica real entrega, e o QR code nele leva o cliente direto à consulta do andamento, sem digitar o código.

## What Changes

- **Comprovante de entrada** para toda ordem: dados da assistência, código, data de abertura, cliente (nome, CPF mascarado e telefone), equipamento (com número de série), problema relatado, previsão de entrega e espaço para assinaturas.
- **Comprovante de entrega** para ordens entregues: acrescenta serviços e peças, totais, pagamentos, data da entrega e "Garantia até".
- **QR code** no comprovante com o endereço da consulta pública da ordem (`/consulta/<código>`).
- **Consulta pública por link:** a página `/consulta/<código>` abre a consulta já preenchida, com os mesmos dados limitados da consulta da página inicial.
- **Impressão e PDF:** botão "Imprimir / salvar PDF" que usa a impressão do navegador, com folha própria para impressão (sem menus, fundo claro, uma página A4).
- Disponível para a equipe no detalhe da ordem e para o cliente no portal (somente as próprias ordens).
- Endereço público configurável por `ASSISTENCIA_PUBLIC_URL`; sem ele, usa o endereço pelo qual o sistema foi acessado.

## Capabilities

### New Capabilities

- `order-receipts`: comprovantes de entrada e de entrega com QR code.

### Modified Capabilities

- `service-orders`: consulta pública por link.

## Impact

- **Código:** `domain/receipt.py`, presenters, estados e páginas do comprovante e da consulta por link, `config.py`, rotas, CSS de impressão.
- **Dependência:** `segno` (gera o QR code em SVG, sem dependências próprias, licença BSD).
- **Backend:** nenhuma mudança; o comprovante usa as leituras já existentes.
- **Testes:** domínio, presenters, permissões e consulta por link.

## Out of Scope

- Geração do PDF no servidor (o PDF sai da impressão do navegador).
- Envio do comprovante por e-mail ou WhatsApp.
- Assinatura digital.
