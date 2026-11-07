# Tasks

## 1. Senhas, limitador e permissões (domínio)

- [x] 1.1 Implementar `domain/passwords.py` (hash PBKDF2-SHA256 com sal, verificação com `compare_digest`, política de senha); verificar com testes de hash diferente para a mesma senha, verificação correta e incorreta, formato armazenado e senhas fracas recusadas.
- [x] 1.2 Implementar `domain/login_throttle.py` com relógio injetável; verificar com testes de bloqueio na sexta tentativa, de desbloqueio após 5 minutos e de janela de 15 minutos.
- [x] 1.3 Implementar `domain/permissions.py` (perfis, permissões, matriz, permissões por transição de status, escopo do técnico); verificar com testes que percorrem cada célula da matriz da proposta.

## 2. Usuários, sessões e serviço de autenticação

- [x] 2.1 Criar o modelo `UserAccount`, o `UserRepository` de demonstração e os usuários de teste com hashes precalculados; verificar com teste de que cada perfil tem uma conta e de que as senhas documentadas são aceitas.
- [x] 2.2 Implementar `data/sessions.py` (token opaco, expiração por inatividade, revogação); verificar com testes de criação, renovação, expiração após 2 horas e token desconhecido.
- [x] 2.3 Implementar `services/auth.py` (login com mensagem genérica e limitador, logout, cadastro de cliente com conta e confirmação de senha, `Principal`); verificar com testes de cada cenário da spec `user-auth`.
- [x] 2.4 Incluir `auth.login`, `auth.register` e `auth.me` em `OPERATIONS` e o provedor Xano sem contrato; verificar com o teste de que nenhuma requisição é enviada.

## 3. Autorização nos serviços

- [x] 3.1 Fazer `ClientService`, `EquipmentService` e `OrderService` receberem `Principal` e exigirem as permissões; verificar com testes de recusa por perfil sem alteração de dados.
- [x] 3.2 Aplicar o escopo do técnico e as permissões por transição de status em `OrderService`; verificar com testes dos cenários da spec `access-control`.
- [x] 3.3 Registrar o nome e o perfil do usuário como autor do histórico; verificar com teste de que o evento traz "Nome (Perfil)".
- [x] 3.4 Implementar `services/portal.py` (ordens do próprio cliente, detalhe sem dados internos, CPF mascarado); verificar com testes dos cenários da spec `customer-portal`.

## 4. Sessão no estado e proteção de rotas

- [x] 4.1 Adicionar o cookie de sessão e os auxiliares de usuário autenticado ao estado; verificar importando o app e com `pytest`.
- [x] 4.2 Proteger todas as páginas `/admin` com guarda de sessão e permissão antes de carregar dados, incluindo o retorno seguro pelo parâmetro `proximo`; verificar no navegador sem sessão, com perfil Cliente e com cada perfil de colaborador.
- [x] 4.3 Criar a página `/acesso-negado`; verificar no navegador com perfil Cliente abrindo `/admin`.

## 5. Login, cadastro e logout

- [x] 5.1 Implementar o login real com mensagens, carregamento, bloqueio e acesso rápido de demonstração; verificar no navegador com credenciais corretas, incorretas e após 5 tentativas.
- [x] 5.2 Implementar o cadastro de cliente com confirmação de senha e entrada automática no portal; verificar no navegador com cadastro válido, senha fraca, senhas diferentes e e-mail repetido.
- [x] 5.3 Implementar o logout no menu público e na barra lateral; verificar no navegador que após sair as páginas administrativas levam ao login.

## 6. Interface conforme o perfil

- [x] 6.1 Exibir nome e perfil do usuário e itens de menu conforme as permissões; verificar no navegador com cada perfil.
- [x] 6.2 Ocultar formulários e botões não permitidos em clientes, equipamentos e ordens, e limitar o seletor de status às transições do perfil; verificar no navegador como Técnico e como Atendente.
- [x] 6.3 Ajustar o menu público (visitante e usuário autenticado); verificar no navegador nos dois casos.

## 7. Portal do cliente

- [x] 7.1 Criar `/minha-conta` com dados da conta e lista das próprias ordens; verificar no navegador com cliente com ordens e com cliente recém-cadastrado.
- [x] 7.2 Criar `/minha-conta/ordens/[codigo]` com orçamento, valores, pagamentos e andamento; verificar no navegador com ordem própria e com código de outro cliente.

## 8. Documentação e verificação integrada

- [x] 8.1 Criar `docs/DEMO_USERS.md` com as contas de demonstração e a matriz de permissões, e atualizar `README.md`, `REQUIREMENTS.md`, `XANO_INTEGRATION.md` e `CHANGELOG.md`; verificar conferindo com as specs.
- [x] 8.2 Executar `pytest`, `openspec validate --all --strict`, a contagem de linhas e a busca por credenciais reais, e registrar os resultados neste arquivo.
- [x] 8.3 Percorrer no navegador o roteiro por perfil (atendente abre a OS, técnico diagnostica, atendente aprova e recebe, cliente acompanha no portal) e registrar os resultados neste arquivo.

## Registro de verificação (2026-11-06)

**Testes automatizados (`.venv`, `python -m pytest`):** 268 aprovados, 0 falhas. Novos: `test_auth_domain` (hash e política de senha, limitador, matriz de permissões célula a célula, permissões por transição, escopo do técnico), `test_auth_services` (login, mensagem genérica, bloqueio e desbloqueio, expiração e revogação de sessão, cadastro e recusas, autorização em cada serviço, autoria do histórico, portal), `test_safe_redirect`; `test_xano` cobre 19 operações sem contrato, incluindo `auth.*`.

**Qualidade:** maior arquivo Python com 274 linhas; nenhuma credencial real versionada (as senhas de teste estão identificadas em `data/demo/users.py` e `docs/DEMO_USERS.md`); `openspec validate --all --strict` com 5 itens válidos.

**Defeito encontrado pelos testes e corrigido:** `reset_auth_state` descartava o `SessionStore` recebido porque um store vazio tem `len() == 0` (avaliado como falso em `sessions or ...`).

**Navegador — modo demonstração (roteiro por perfil):**
- Visitante: `/admin/clientes` redireciona para `/login?proximo=/admin/clientes` sem exibir dados; menu público com "Entrar" e "Criar conta".
- Login: senha errada e e-mail inexistente exibem a mesma mensagem "E-mail ou senha inválidos."; login correto do atendente volta para `/admin/clientes`, com cookie de sessão e nome/perfil na barra lateral.
- Atendente: cadastra e edita clientes, sem botão "Excluir"; registra a aprovação da OS-2026-00123 (histórico com "Paulo Nunes (Atendente)"); na OS-2026-00125 (Em reparo) vê apenas "Cancelar ordem", pagamento e troca de técnico, sem diagnóstico e orçamento.
- Logout: limpa o cookie e `/admin` volta a exigir login.
- Técnico (acesso rápido, Carlos): clientes sem cadastro, edição ou exclusão; ordens sem formulário de abertura; na própria OS-2026-00125 vê "Mover para Concluído", edita diagnóstico e orçamento (histórico com "Carlos Mendes (Técnico)"), sem pagamento e com técnico travado; na OS-2026-00124 (Fernanda) vê o aviso de somente consulta e nenhuma ação; `/minha-conta` redireciona para `/admin`.
- Cliente (acesso rápido, Marina): portal com CPF `***.***.***-05` e somente a OS-2026-00125; detalhe com orçamento, valores e andamento, sem autores ou técnicos; OS-2026-00124 pelo endereço mostra "não encontrada"; `/admin` leva a `/acesso-negado`.
- Cadastro: senha fraca, senhas diferentes e e-mail de conta existente recusados; cadastro válido entra no portal sem ordens e o cliente aparece na lista administrativa.
- Bloqueio: após 5 senhas erradas, a senha correta é recusada com "Tente novamente em 5 minuto(s)".
- `proximo=//exemplo.invalid/roubo` é ignorado e o login segue para `/admin`.

**Navegador — modo Xano sem contratos:** acesso rápido oculto; o login informa que a integração com o Xano para entrar no sistema aguarda a documentação oficial; `/admin` continua exigindo login.

**Observações e limitações:**
- A expiração de 2 horas e o fim do bloqueio de 5 minutos foram verificados por testes com relógio simulado, não esperando o tempo real no navegador.
- Ao abrir uma página protegida sem sessão, a estrutura vazia da página aparece por um instante antes do redirecionamento; nenhum dado é enviado, porque a guarda roda antes do carregamento.
- Sessões, bloqueios e contas criadas em `/cadastro` ficam em memória e se perdem ao reiniciar o servidor (inclusive no hot reload).
- O cookie de sessão não é `HttpOnly` (limitação do Reflex), mitigado por `SameSite=Strict`, token opaco revogável e expiração.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
