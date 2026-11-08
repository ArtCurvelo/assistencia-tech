# Design: Comprovante da ordem com QR code

## Decisions

### D1. Tipo do comprovante pelo status

Ordem Entregue gera "Comprovante de entrega"; qualquer outro status gera "Comprovante de entrada". Ordem cancelada mostra o status e o motivo do cancelamento no comprovante de entrada. A regra fica em `domain/receipt.py`, junto com a montagem do endereço da consulta.

### D2. PDF pela impressão do navegador

O comprovante é uma página HTML com folha de estilos de impressão (`@media print`): esconde a barra de ações e a navegação, usa fundo branco e cabe numa página A4. O botão "Imprimir / salvar PDF" chama `window.print()`; todo navegador atual oferece "Salvar como PDF". Gerar o PDF no servidor exigiria bibliotecas com dependências nativas (fontes, imagens) para o mesmo resultado.

### D3. QR code em SVG gerado no servidor

`segno` gera o QR code como SVG embutido (`data:image/svg+xml`), sem serviço externo: o código da ordem não sai do sistema para montar a imagem. O nível mínimo de correção é "M", que tolera pequenas falhas de impressão.

### D4. Endereço da consulta

`ASSISTENCIA_PUBLIC_URL` define o endereço público (na publicação, o domínio do site). Sem ela, usa o endereço pelo qual a página foi aberta. Em `localhost`, o QR code só funciona no próprio computador; isso é dito na documentação. A consulta por link aceita somente o formato `OS-AAAA-NNNNN`, para não repassar texto livre ao backend.

### D5. Dados exibidos

- Equipe (permissão `orders.view`): nome, CPF mascarado (`***.***.***-NN`) e telefone do cliente. O CPF completo não vai para o papel, que pode se perder.
- Cliente no portal: o mesmo comprovante, montado a partir das próprias ordens (`PortalService.my_order`); ordem de outro cliente recebe "não encontrada".
- Nenhum comprovante mostra autores do histórico, diagnóstico interno ou dados de outros clientes.

## Risks / Trade-offs

- [Impressão diferente entre navegadores] → layout simples em blocos, conferido no Chrome; margens definidas por `@page`.
- [QR com `localhost` durante o desenvolvimento] → documentado; resolvido com `ASSISTENCIA_PUBLIC_URL` na publicação (incremento de deploy).
