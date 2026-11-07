# Contas de demonstração e perfis de acesso

> **Somente para o modo demonstração.** As senhas abaixo são de **teste**, públicas por definição e válidas apenas nos dados fictícios em memória. Elas não existem em nenhum backend real e não devem ser reutilizadas em outros sistemas. Com a fonte Xano, estas contas e o acesso rápido não ficam disponíveis.

Na tela de login (`/login`), o bloco **Acesso rápido** entra com uma conta de cada perfil sem digitar senha. A senha de teste é lida no servidor e nunca é enviada ao navegador.

## Contas

| Perfil | Nome | E-mail | Senha de teste | Vínculo |
|---|---|---|---|---|
| Administrador | Ana Ribeiro | `admin@assistencia.test` | `admin2026` | — |
| Atendente | Paulo Nunes | `atendimento@assistencia.test` | `atende2026` | — |
| Técnico | Carlos Mendes | `carlos@assistencia.test` | `tecnico2026` | Técnico 1 (computadores e notebooks) |
| Técnico | Fernanda Rocha | `fernanda@assistencia.test` | `tecnico2026` | Técnico 2 (consoles) |
| Técnico | Diego Martins | `diego@assistencia.test` | `tecnico2026` | Técnico 3 (celulares e tablets) |
| Cliente | Marina Oliveira | `marina@example.test` | `cliente2026` | Cliente 1 (OS-2026-00125) |
| Cliente | Camila Souza | `camila@example.test` | `cliente2026` | Cliente 3 (OS-2026-00120) |

As senhas ficam armazenadas apenas como hash PBKDF2-SHA256 com sal (600.000 iterações), em `assistencia_tech/data/demo/users.py`.

Novas contas de cliente podem ser criadas em `/cadastro`; a senha precisa ter no mínimo 8 caracteres, com letras e números.

## Matriz de permissões

| Ação | Administrador | Atendente | Técnico | Cliente |
|---|:-:|:-:|:-:|:-:|
| Ver painel, clientes, equipamentos e ordens | ✓ | ✓ | ✓ | — |
| Cadastrar e editar clientes e equipamentos | ✓ | ✓ | — | — |
| Excluir clientes e equipamentos | ✓ | — | — | — |
| Abrir ordens e atribuir técnico | ✓ | ✓ | — | — |
| Diagnóstico e orçamento | ✓ | — | ✓ (somente as suas) | — |
| Iniciar análise, enviar para aprovação, concluir reparo | ✓ | — | ✓ (somente as suas) | — |
| Registrar aprovação (Aguardando aprovação → Em reparo) | ✓ | ✓ | — | — |
| Registrar pagamentos e entregar | ✓ | ✓ | — | — |
| Cancelar ordens | ✓ | ✓ | — | — |
| Consultar relatórios e exportar CSV (`/admin/relatorios`) | ✓ | ✓ | — | — |
| Gerenciar colaboradores (`/admin/colaboradores`) | ✓ | — | — | — |
| Portal com as próprias ordens (`/minha-conta`) | — | — | — | ✓ |

A matriz é definida em `assistencia_tech/domain/permissions.py` (`ROLE_PERMISSIONS`) e verificada em `tests/test_auth_domain.py`, que percorre cada célula. As permissões são aplicadas **nos serviços**: uma ação não permitida é recusada mesmo que a interface seja contornada.

## Segurança da sessão

- O login usa a mesma mensagem genérica para e-mail inexistente e senha incorreta.
- Após 5 tentativas erradas em 15 minutos, o e-mail fica bloqueado por 5 minutos.
- A sessão é identificada por um token aleatório em cookie `SameSite=Strict`, validado no servidor, e expira após 2 horas sem atividade.
- O parâmetro `proximo` do login aceita somente caminhos internos (evita redirecionamento aberto).
- Limitação conhecida: o cookie não é `HttpOnly`, porque o Reflex lê cookies pelo navegador; o token é opaco, revogável no logout e não carrega dados pessoais.


## Contas de teste no Xano (workspace 170741)

Criadas na verificação de 07/11/2026 (tarefa 6.5 de `integrate-xano-backend`). As senhas foram geradas aleatoriamente e **não** são versionadas; o administrador pode redefini-las em Colaboradores → Senha.

| Nome | E-mail | Perfil |
|---|---|---|
| Paula Atendente (teste) | atendente.roteiro@exemplo.test | Atendente |
| Carlos Mendes (teste) | tecnico.roteiro@exemplo.test | Técnico (Notebooks) |
| Joana Teixeira | joana.roteiro@exemplo.test | Cliente |

O domínio `exemplo.test` não recebe e-mails.
