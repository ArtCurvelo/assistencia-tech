# Proposal: Autenticação, perfis de acesso e portal do cliente

## Why

Hoje qualquer visitante acessa `/admin`, o link "Painel" aparece no menu público, o login e o cadastro são apenas de fachada e o histórico da OS registra "Usuário demonstração" como autor. Uma aplicação de assistência técnica precisa identificar quem opera o sistema, limitar cada pessoa ao que o cargo permite e oferecer ao cliente um acesso próprio para acompanhar seus equipamentos. Com o domínio completo pronto (`expand-service-domain`), as regras de acesso podem ser aplicadas a cada operação real.

## What Changes

- **Login e logout** com e-mail e senha, sessão no servidor com expiração por inatividade, mensagem genérica para credenciais inválidas e bloqueio temporário após tentativas sucessivas.
- **Cadastro de cliente** (autoatendimento): cria o cliente, com as mesmas validações de CPF, e-mail e telefone, e a conta de acesso, com política mínima de senha.
- **Senhas** armazenadas apenas como hash com sal (PBKDF2-SHA256), nunca em texto puro.
- **Perfis de acesso** com uma matriz de permissões (abaixo), aplicada tanto na interface (menus e botões) quanto nos serviços de aplicação (a operação é recusada mesmo que a interface seja contornada).
- **Proteção de rotas:** páginas administrativas exigem autenticação e permissão; o visitante é levado ao login e volta à página pretendida depois de entrar; sem permissão, vê uma página de acesso negado.
- **Escopo do técnico:** o técnico só altera as ordens em que é o responsável.
- **Portal do cliente** (`/minha-conta`): o cliente vê apenas as próprias ordens, com status, orçamento, valores e andamento.
- **Autoria real no histórico:** os eventos da OS passam a registrar o nome e o perfil de quem fez a alteração.
- **Modo demonstração:** usuários de teste para cada perfil, identificados como demonstrativos, com acesso rápido na tela de login somente nesse modo.
- **Xano:** a autenticação fica atrás de uma interface interna; o adaptador Xano permanece sem contrato e falha de forma explícita até a documentação oficial.

### Perfis e permissões propostos

| Ação | Administrador | Atendente | Técnico | Cliente |
|---|:-:|:-:|:-:|:-:|
| Ver painel administrativo | ✓ | ✓ | ✓ | — |
| Ver clientes e equipamentos | ✓ | ✓ | ✓ | — |
| Cadastrar e editar clientes e equipamentos | ✓ | ✓ | — | — |
| Excluir clientes e equipamentos | ✓ | — | — | — |
| Ver todas as ordens | ✓ | ✓ | ✓ | — |
| Abrir ordens e atribuir técnico | ✓ | ✓ | — | — |
| Diagnóstico e orçamento | ✓ | — | ✓ (somente as suas) | — |
| Status técnico: iniciar análise, enviar para aprovação, concluir reparo | ✓ | — | ✓ (somente as suas) | — |
| Registrar aprovação do orçamento (Aguardando aprovação → Em reparo) | ✓ | ✓ | — | — |
| Registrar pagamentos e entregar | ✓ | ✓ | — | — |
| Cancelar ordens | ✓ | ✓ | — | — |
| Ver as próprias ordens no portal | — | — | — | ✓ |

## Capabilities

### New Capabilities

- `user-auth`: login, logout, sessão, cadastro de cliente, armazenamento de senhas, política de senha e bloqueio por tentativas.
- `access-control`: perfis, matriz de permissões, proteção de rotas, verificação nas operações e escopo do técnico.
- `customer-portal`: área do cliente com as próprias ordens de serviço.

### Modified Capabilities

- Nenhuma especificação vigente em `openspec/specs/` muda. A autoria do histórico (requisito da mudança ainda não arquivada `expand-service-domain`) continua válida; esta mudança apenas passa a preenchê-la com o usuário autenticado.

## Impact

- **Código:** novos `domain/permissions.py`, `services/auth.py`, repositório de usuários e armazenamento de sessões em `data/`; serviços de clientes, equipamentos e ordens passam a receber o usuário autenticado; estado raiz ganha a sessão (cookie); páginas de login, cadastro, acesso negado e portal; menus e botões condicionados a permissões.
- **Dados de demonstração:** usuários de teste com hashes de senha precalculados.
- **Testes:** hash e verificação de senha, política de senha, bloqueio, expiração de sessão, matriz de permissões, escopo do técnico e recusa nas operações dos serviços.

## Assumptions

- Perfis e permissões conforme a tabela acima (revisáveis antes da implementação).
- Sessão expira após 2 horas sem atividade; cookie de sessão com `SameSite=Strict`.
- Bloqueio de 5 minutos após 5 tentativas de login malsucedidas para o mesmo e-mail em 15 minutos.
- Senha com no mínimo 8 caracteres, contendo letras e números.
- As contas de colaboradores (administrador, atendente, técnicos) vêm dos dados de demonstração; o cadastro e a gestão de colaboradores ficam para a mudança de administração.

## Out of Scope

- Gerenciamento de colaboradores, cargos e permissões pela interface (mudança de administração).
- Recuperação de senha por e-mail, verificação de e-mail e autenticação em dois fatores.
- Persistência de sessões entre reinícios do servidor.
- Qualquer endpoint ou fluxo de autenticação do Xano não documentado oficialmente.
