# Roteiro de apresentação (≈ 12 minutos)

Roteiro para apresentar o sistema **publicado**, com o backend real no Xano. (O `DEMO_SCRIPT.md` é o roteiro antigo, do modo demonstração local.)

## Antes de começar (10 minutos antes)

1. Abra https://assistencia-tech-2eyb.onrender.com para acordar o site (em horário comercial ele já deve estar acordado).
2. Tenha à mão as contas (as senhas das contas de teste estão nos arquivos locais gerados pelo povoamento, fora do repositório):
   - **administrador:** a sua conta;
   - **técnico:** um dos técnicos de vitrine;
   - **cliente:** um cliente de vitrine com ordem **Aguardando aprovação** e outro com ordem **Entregue** (veja no Quadro de ordens quem são).
3. Abra três janelas: uma normal (administrador), uma anônima (técnico) e outra de outro navegador ou perfil (cliente). Assim você troca de papel sem sair da conta.
4. Deixe o celular pronto para ler um QR code.
5. Abra em outra aba: o repositório no GitHub (aba **Actions**) e o painel do Xano (tabelas).

> O Xano gratuito aceita 10 requisições a cada 20 segundos. Navegue sem pressa entre as telas; se aparecer "O serviço está indisponível no momento", espere 10 segundos e repita.

## Roteiro

| # | Tempo | O que mostrar | O que dizer |
|---|---|---|---|
| 1 | 1 min | **Página inicial**: números, consulta de ordem; **Serviços**: etapas e perguntas frequentes | "Os números da página inicial são reais: vêm de um endpoint público do backend que só devolve contagens, sem dado pessoal." |
| 2 | 1 min | **Painel** (administrador): saudação, "Precisa de atenção", indicadores, gráficos | "O painel não mostra só números: ele diz o que fazer agora, por prioridade." |
| 3 | 2 min | **Abrir uma ordem** para um cliente de vitrine → **Comprovante** → imprimir/PDF → ler o **QR code** no celular | "O cliente sai com o comprovante. O QR code abre a consulta pública, que não mostra nome, CPF nem valores. O CPF no papel sai mascarado." |
| 4 | 2 min | Janela do **técnico**: "Meus atendimentos" → Em análise → diagnóstico → serviço + **peça do estoque** → Aguardando aprovação | "A peça saiu do estoque na hora, na mesma transação. O técnico só mexe nas ordens dele: tente abrir a de outro técnico e os botões somem." |
| 5 | 2 min | Janela do **cliente**: orçamento no portal → **Aprovar** (ou recusar em outra ordem, com motivo) | "Quem aprova é o próprio cliente. Nem o administrador consegue aprovar em nome dele: essa permissão é só do perfil cliente." |
| 6 | 1 min | **Quadro de ordens**: mover para Concluído; tentar **Entregue** sem pagamento (recusa); registrar o pagamento; entregar | "A regra de negócio barra a entrega sem quitação — na aplicação e de novo no backend." |
| 7 | 1 min | Cliente: **avaliar** a ordem entregue (nota e comentário); administrador: **Relatórios** → NPS, evolução mensal, PDF | "A avaliação é única por ordem e alimenta o NPS, a métrica de satisfação mais usada no mercado." |
| 8 | 1 min | Cliente: **Privacidade e dados (LGPD)** → baixar os dados; mostrar o diálogo de exclusão (sem confirmar) | "O titular baixa os dados e pode excluir a conta: o cadastro é anonimizado e as ordens ficam, como a lei permite." |
| 9 | 1 min | **GitHub → Actions**: testes, contrato com o Xano, OpenSpec e ponta a ponta no navegador, todos verdes; **Xano**: tabelas | "Cada envio roda mais de 470 testes, confere o contrato com o backend e abre o site num navegador real. O deploy é automático." |

## Se sobrar tempo

- **Garantia:** abrir uma ordem em garantia a partir de uma ordem entregue (sai sem cobrança e ligada à original).
- **Estoque:** alerta de estoque baixo no painel e a lista de movimentações.
- **Teclado:** na página inicial, apertar Tab e mostrar o "Pular para o conteúdo" e o foco visível.
- **OpenSpec:** abrir `openspec/specs/service-orders/spec.md` e mostrar um requisito com os cenários, e a mudança arquivada com o registro do que foi testado.

## Plano de contingência

| Problema | O que fazer |
|---|---|
| Site demorando a abrir | Está acordando (até 1 minuto). Enquanto isso, mostre o GitHub ou o Xano |
| "O serviço está indisponível no momento" | Limite do Xano gratuito: espere 10 segundos e repita |
| Sessão caiu | O site reiniciou: entre de novo |
| Site fora do ar | Rode localmente: `.venv\Scripts\reflex.exe run` (modo demonstração, com acesso rápido às contas) e siga o `DEMO_SCRIPT.md` |
| Internet ruim | Mesmo plano local; o modo demonstração não precisa de internet depois de instalado |

## Perguntas prováveis

- **"Onde ficam as regras?"** Nos dois lados: `domain/` na aplicação e XanoScript no backend. A tabela está em `VISAO_DO_SISTEMA.md`.
- **"Como você sabe que funciona?"** Testes automáticos, verificador de contrato, testes no navegador e o registro de verificação de cada mudança no OpenSpec.
- **"E a segurança?"** Sem credenciais no código; token de cada usuário guardado no servidor; permissões conferidas em toda operação; consulta pública sem dado pessoal; CPF mascarado; LGPD no portal.
- **"O que não foi feito?"** Recuperação de senha e avisos por e-mail (dependem de um serviço de e-mail) e a sugestão de diagnóstico por IA (depende de uma chave paga).
