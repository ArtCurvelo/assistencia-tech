# Tasks

## 1. Senhas, limitador e permissões (domínio)

- [ ] 1.1 Implementar `domain/passwords.py` (hash PBKDF2-SHA256 com sal, verificação com `compare_digest`, política de senha); verificar com testes de hash diferente para a mesma senha, verificação correta e incorreta, formato armazenado e senhas fracas recusadas.
- [ ] 1.2 Implementar `domain/login_throttle.py` com relógio injetável; verificar com testes de bloqueio na sexta tentativa, de desbloqueio após 5 minutos e de janela de 15 minutos.
- [ ] 1.3 Implementar `domain/permissions.py` (perfis, permissões, matriz, permissões por transição de status, escopo do técnico); verificar com testes que percorrem cada célula da matriz da proposta.

## 2. Usuários, sessões e serviço de autenticação

- [ ] 2.1 Criar o modelo `UserAccount`, o `UserRepository` de demonstração e os usuários de teste com hashes precalculados; verificar com teste de que cada perfil tem uma conta e de que as senhas documentadas são aceitas.
- [ ] 2.2 Implementar `data/sessions.py` (token opaco, expiração por inatividade, revogação); verificar com testes de criação, renovação, expiração após 2 horas e token desconhecido.
- [ ] 2.3 Implementar `services/auth.py` (login com mensagem genérica e limitador, logout, cadastro de cliente com conta e confirmação de senha, `Principal`); verificar com testes de cada cenário da spec `user-auth`.
- [ ] 2.4 Incluir `auth.login`, `auth.register` e `auth.me` em `OPERATIONS` e o provedor Xano sem contrato; verificar com o teste de que nenhuma requisição é enviada.

## 3. Autorização nos serviços

- [ ] 3.1 Fazer `ClientService`, `EquipmentService` e `OrderService` receberem `Principal` e exigirem as permissões; verificar com testes de recusa por perfil sem alteração de dados.
- [ ] 3.2 Aplicar o escopo do técnico e as permissões por transição de status em `OrderService`; verificar com testes dos cenários da spec `access-control`.
- [ ] 3.3 Registrar o nome e o perfil do usuário como autor do histórico; verificar com teste de que o evento traz "Nome (Perfil)".
- [ ] 3.4 Implementar `services/portal.py` (ordens do próprio cliente, detalhe sem dados internos, CPF mascarado); verificar com testes dos cenários da spec `customer-portal`.

## 4. Sessão no estado e proteção de rotas

- [ ] 4.1 Adicionar o cookie de sessão e os auxiliares de usuário autenticado ao estado; verificar importando o app e com `pytest`.
- [ ] 4.2 Proteger todas as páginas `/admin` com guarda de sessão e permissão antes de carregar dados, incluindo o retorno seguro pelo parâmetro `proximo`; verificar no navegador sem sessão, com perfil Cliente e com cada perfil de colaborador.
- [ ] 4.3 Criar a página `/acesso-negado`; verificar no navegador com perfil Cliente abrindo `/admin`.

## 5. Login, cadastro e logout

- [ ] 5.1 Implementar o login real com mensagens, carregamento, bloqueio e acesso rápido de demonstração; verificar no navegador com credenciais corretas, incorretas e após 5 tentativas.
- [ ] 5.2 Implementar o cadastro de cliente com confirmação de senha e entrada automática no portal; verificar no navegador com cadastro válido, senha fraca, senhas diferentes e e-mail repetido.
- [ ] 5.3 Implementar o logout no menu público e na barra lateral; verificar no navegador que após sair as páginas administrativas levam ao login.

## 6. Interface conforme o perfil

- [ ] 6.1 Exibir nome e perfil do usuário e itens de menu conforme as permissões; verificar no navegador com cada perfil.
- [ ] 6.2 Ocultar formulários e botões não permitidos em clientes, equipamentos e ordens, e limitar o seletor de status às transições do perfil; verificar no navegador como Técnico e como Atendente.
- [ ] 6.3 Ajustar o menu público (visitante e usuário autenticado); verificar no navegador nos dois casos.

## 7. Portal do cliente

- [ ] 7.1 Criar `/minha-conta` com dados da conta e lista das próprias ordens; verificar no navegador com cliente com ordens e com cliente recém-cadastrado.
- [ ] 7.2 Criar `/minha-conta/ordens/[codigo]` com orçamento, valores, pagamentos e andamento; verificar no navegador com ordem própria e com código de outro cliente.

## 8. Documentação e verificação integrada

- [ ] 8.1 Criar `docs/DEMO_USERS.md` com as contas de demonstração e a matriz de permissões, e atualizar `README.md`, `REQUIREMENTS.md`, `XANO_INTEGRATION.md` e `CHANGELOG.md`; verificar conferindo com as specs.
- [ ] 8.2 Executar `pytest`, `openspec validate --all --strict`, a contagem de linhas e a busca por credenciais reais, e registrar os resultados neste arquivo.
- [ ] 8.3 Percorrer no navegador o roteiro por perfil (atendente abre a OS, técnico diagnostica, atendente aprova e recebe, cliente acompanha no portal) e registrar os resultados neste arquivo.

## Workflow follow-up

- Arquivar esta mudança após a verificação integrada e a revisão do usuário.
