# Design: Autoatendimento do cliente e avisos

## Decisions

### D1. Status "Solicitado" antes de "Recebido"

"Recebido" significa que o equipamento está na assistência. Uma ordem pedida pelo portal ainda não tem equipamento, então nasce em **Solicitado**, sem previsão de entrega. Transições: Solicitado → Recebido (permissão de abrir ordens: Administrador e Atendente) ou → Cancelado (com motivo). Ao confirmar o recebimento, a previsão vira hoje + 7 dias. Solicitado não conta como atraso nem como "em atendimento" nos números públicos.

### D2. Entrega

`delivery_mode` é "Levar à loja" ou "Coleta por motoboy". Na coleta, o endereço (até 200 caracteres) e o período (Manhã, Tarde ou Noite) são obrigatórios. Ordens abertas no balcão não têm forma de entrega. O endereço da loja vem de `ASSISTENCIA_STORE_ADDRESS` e o horário de `ASSISTENCIA_STORE_HOURS`; sem configuração, o portal diz que o endereço será confirmado pela assistência — o sistema não inventa endereço.

### D3. Equipamentos pelo portal

O cliente só cria e vê equipamentos do próprio cadastro: o backend usa o cliente do token, nunca um identificador enviado pelo navegador. O número de série, quando informado, continua único (conferido no backend).

### D4. Avisos por e-mail fora da transação

Depois de uma operação concluída (abertura, solicitação, mudança de status, decisão do orçamento), o serviço monta a mensagem e chama o `Notifier`. Falha no envio é registrada no log e **não** desfaz a operação. O envio real usa a API HTTP do Brevo (`POST https://api.brevo.com/v3/smtp/email`) com `BREVO_API_KEY` e o remetente `ASSISTENCIA_EMAIL_FROM`; sem essas variáveis, ou no modo demonstração, nada é enviado. Endereços de domínios reservados (`.test`, `.invalid`, `.example`, `example.*`) e cadastros anonimizados são ignorados, para não enviar a contas fictícias.

### D5. Conteúdo do aviso

Assunto e texto com o código da ordem, o novo status, uma frase do que acontece agora e o link da consulta pública. Nada de valores, diagnóstico ou dados pessoais além do primeiro nome.

### D6. WhatsApp por link

O botão "Avisar pelo WhatsApp" usa `https://wa.me/55<telefone>?text=<mensagem>`: abre o WhatsApp de quem atende com a mesma mensagem do e-mail. O envio é manual e gratuito.

## Risks / Trade-offs

- [E-mail cair no spam] → remetente verificado no Brevo e texto simples; a consulta pública e o portal continuam como fonte do andamento.
- [Mais um status em todas as telas] → coberto por testes de fluxo, quadro e ponta a ponta.
