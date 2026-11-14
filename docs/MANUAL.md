# Manual de uso

Site: https://assistencia-tech-2eyb.onrender.com — o primeiro acesso depois de um tempo parado pode levar cerca de 1 minuto.

Cada pessoa vê só o que o seu perfil permite. O sistema tem quatro perfis: **Cliente**, **Atendente**, **Técnico** e **Administrador**.

## Visitante (sem login)

- **Página inicial:** apresentação, números reais do sistema (equipamentos entregues, em atendimento, satisfação) e a consulta de ordem.
- **Consultar uma ordem:** digite o código (por exemplo, `OS-2026-00012`) em "Acompanhe seu equipamento", ou leia o QR code do comprovante. Aparecem só o status, o equipamento, a previsão e a última atualização — nenhum dado pessoal ou valor.
- **Serviços:** o que a assistência faz, as etapas do atendimento e as dúvidas frequentes.
- **Criar conta:** nome, CPF, e-mail, telefone e senha (mínimo de 8 caracteres, com letras e números).

## Cliente

Depois de entrar, o cliente cai em **Minha conta**.

| Quero… | Como |
|---|---|
| Ver minhas ordens | Lista em "Minhas ordens de serviço"; clique no código para o detalhe |
| Aprovar ou recusar um orçamento | No detalhe de uma ordem "Aguardando aprovação": **Aprovar orçamento** inicia o reparo; **Recusar orçamento** pede o motivo e cancela a ordem |
| Pegar o comprovante | No detalhe da ordem, **🧾 Comprovante (imprimir / PDF)** |
| Avaliar o atendimento | No detalhe de uma ordem entregue: escolha a nota de 0 a 10, comente se quiser e envie. A avaliação é única e não pode ser alterada |
| Baixar meus dados | Em "Privacidade e dados (LGPD)", **Baixar meus dados (JSON)** |
| Excluir minha conta | No mesmo quadro, **Excluir minha conta**: confirme com a senha e digite EXCLUIR. Só é possível sem ordens em andamento. Nome, CPF, e-mail e telefone são anonimizados; as ordens continuam registradas sem identificar você |

## Atendente

Entra pelo mesmo "Entrar" e cai no **painel**.

| Quero… | Como |
|---|---|
| Saber o que fazer agora | Painel → "Precisa de atenção": atrasadas, prontas para entrega e aguardando o cliente |
| Cadastrar cliente e equipamento | Menu **Clientes** e **Equipamentos** |
| Abrir uma ordem | **Ordens de serviço** → "Abrir ordem de serviço": cliente, equipamento, problema e previsão (padrão de 7 dias) |
| Entregar o comprovante de entrada | No detalhe da ordem, **🧾 Comprovante** → **Imprimir / salvar PDF** |
| Definir o técnico e a previsão | No detalhe da ordem |
| Acompanhar o fluxo | **Quadro de ordens**: uma coluna por status; "→ Em reparo", "→ Entregue" movem a ordem |
| Registrar a aprovação pelo balcão | No detalhe ou no quadro: "Em reparo" numa ordem aguardando aprovação |
| Receber e entregar | No detalhe: registre o pagamento e mova para **Entregue**. O sistema recusa a entrega com saldo em aberto |
| Abrir ordem em garantia | No detalhe de uma ordem entregue há até 90 dias: **Abrir ordem em garantia** (sem cobrança) |
| Cancelar | No detalhe: **Cancelar ordem**, com o motivo. As peças voltam ao estoque |
| Cuidar do estoque | **Estoque**: cadastrar peça, registrar entrada, ver movimentações e alertas de estoque baixo |
| Tirar relatórios | **Relatórios**: período, indicadores, evolução mensal, NPS, **Exportar CSV** e **Imprimir / salvar PDF** |

## Técnico

| Quero… | Como |
|---|---|
| Ver minha fila | Painel → "Meus atendimentos" (ordens em aberto atribuídas a mim, as mais antigas primeiro) |
| Começar a análise | No detalhe ou no quadro: mover para **Em análise** |
| Registrar diagnóstico e orçamento | No detalhe: diagnóstico, serviços e peças. Peça do estoque dá baixa automática; sem estoque, o sistema recusa |
| Enviar o orçamento ao cliente | Mover para **Aguardando aprovação** |
| Concluir o reparo | Depois da aprovação, mover para **Concluído** |

O técnico consulta todas as ordens, mas só altera as que estão atribuídas a ele. Não registra pagamentos, não entrega e não altera a previsão.

## Administrador

Faz tudo o que a atendente e o técnico fazem, e ainda:

- **Colaboradores:** cria contas (com senha provisória), muda o perfil e a especialidade, redefine senha, desativa e reativa. O sistema impede a desativação do último administrador e de técnico com ordens em aberto.
- Não acessa o portal do cliente nem decide orçamento ou avalia em nome do cliente: essas ações são só do próprio cliente.

## Status de uma ordem

```
Recebido → Em análise → Aguardando aprovação → Em reparo → Concluído → Entregue
                                    ↓ (recusa do cliente)
        (em qualquer etapa antes da entrega) → Cancelado
```

Cada mudança fica no **histórico** da ordem, com data, autor e descrição, e não pode ser apagada.

## Mensagens comuns

| Mensagem | O que significa |
|---|---|
| "Há saldo a receber… Registre o pagamento antes da entrega." | A ordem precisa estar quitada para ser entregue |
| "Estoque insuficiente…" | A peça escolhida não tem a quantidade pedida; registre uma entrada ou use peça avulsa |
| "Esta ordem pertence a outro técnico…" | Técnicos só alteram as próprias ordens |
| "O serviço está indisponível no momento…" | O Xano gratuito atingiu o limite de requisições; aguarde alguns segundos |
| "Sua sessão expirou por inatividade…" | Duas horas sem atividade ou reinício do site; entre de novo |
