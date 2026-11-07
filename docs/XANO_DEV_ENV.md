# Ambiente de desenvolvimento do backend Xano

Configuração adotada a partir do *Manual de Instalação e Configuração do Ambiente Xano + VS Code + Git + IA* da disciplina. O backend passa a ser mantido como código XanoScript versionado neste repositório, seguindo o mesmo processo das demais mudanças: especificação → código → validação → `git diff` → commit → envio.

## Ferramentas (verificadas em 07/11/2026)

| Ferramenta | Versão | Origem | Situação |
|---|---|---|---|
| Node.js | v24.20.0 | — | instalado |
| Xano CLI (`@xano/cli`) | 1.3.4 | npm, organização `xano-inc`, mantenedores `@xano.com` | instalado globalmente |
| Xano Developer MCP (`@xano/developer-mcp`) | 2.2.6 (fixada) | npm, organização `xano-inc` | configurado; 7 ferramentas respondendo |

Configuração do MCP:

- `.mcp.json`: Claude Code. Carregado ao iniciar a sessão; aprove o servidor `xano` quando solicitado.
- `.vscode/mcp.json`: VS Code e GitHub Copilot (`Ctrl+Shift+P` → *MCP: List Servers* → `xano` → *Start*).

Ferramentas do Developer MCP: `xano_validate_xanoscript`, `xano_xanoscript_docs`, `xano_cli_docs`, `xano_meta_api_docs`, `xano_knowledge_list`, `xano_knowledge_get` e `xano_version`. O servidor roda localmente e não usa credenciais do Xano.

## Autenticação do CLI (feita pelo dono da conta)

```powershell
xano auth
xano profile me
```

O `xano auth` abre o navegador para o login. As credenciais ficam em `%USERPROFILE%\.xano\credentials.yaml`, **fora do repositório**. Não use a opção `-k/--insecure`: o Node desta máquina valida o certificado do Xano normalmente.

## Sincronização

```powershell
xano workspace pull -d ./xano              # baixa o código do workspace
git diff                                   # revisa as alterações
xano workspace push -d ./xano --dry-run    # simula o envio
```

- **Não** use `--env` nem `--records` no `pull`: variáveis de ambiente podem conter segredos, e os registros contêm dados pessoais (CPF, e-mail). Somente o código e a estrutura vão para o git.
- Envie (`push` sem `--dry-run`) apenas depois de revisar o `git diff` e a simulação, de preferência primeiro para um branch ou sandbox do Xano.
- Depois de cada envio, confira o contrato com `python -m tools.xano_contract_check`.
- Verificador do backend próprio (workspace 170741):
  `python -m tools.xano_contract_check --instance https://x8ki-letl-twmt.n7.xano.io --auth assistencia-tech-auth --cliente assistencia-tech-cliente --os assistencia-tech-os`
  (resultado em 07/11/2026: 27 de 27).
- Para o Swagger documentar a resposta, devolva o resultado direto de `db.get`/`db.query` e escolha os campos com `output = [...]`; respostas montadas com `map`/`unset`, objetos literais, resultado de função ou variáveis definidas dentro de `conditional` aparecem sem esquema.

### Cuidado: `xano workspace edit`

Em 07/11/2026, `xano workspace edit -w 170741 --swagger --no-require-token` (CLI 1.3.4) ligou o Swagger, mas renomeou o workspace e o deixou com o modelo inicial do Xano no lugar do backend enviado. O backend foi restaurado com `xano workspace push -d ./xano --sync --delete` (após simulação e autorização). Depois de qualquer `workspace edit`, confira com `xano workspace pull` para uma pasta temporária e rode o verificador; prefira alterar configurações do workspace pelo painel.

## Segurança

- O MCP usado é o **Developer MCP** (documentação e validação). O *Xano MCP Server*, que opera diretamente no workspace, não foi configurado.
- Nenhum token ou senha é gravado em arquivos do projeto.
- O cliente HTTP da aplicação (Python) usa `truststore` para validar o certificado do Xano pelo repositório do Windows (veja `XANO_INTEGRATION.md`).
