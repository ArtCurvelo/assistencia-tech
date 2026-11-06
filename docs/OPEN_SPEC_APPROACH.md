# Processo de especificação com OpenSpec

## Objetivo deste documento

Este projeto utiliza a ferramenta **OpenSpec** (CLI `openspec`, versão 1.14.3, esquema `spec-driven`) para organizar as mudanças relevantes: cada mudança é proposta, especificada, projetada e dividida em tarefas verificáveis antes da implementação, e as especificações aprovadas passam a compor a documentação viva do sistema.

> Versões anteriores deste documento afirmavam que a ferramenta não era utilizada. Isso deixou de ser verdade a partir da mudança `redesign-interface` (arquivada em 2026-10-29), executada e validada com a CLI.

## Onde estão os artefatos

| Local | Conteúdo |
|---|---|
| `openspec/config.yaml` | Contexto do projeto e regras para os artefatos (idioma, restrições do Xano, verificação das tarefas) |
| `openspec/specs/<capacidade>/spec.md` | Especificações vigentes do sistema (fonte da verdade) |
| `openspec/changes/<mudança>/` | Mudanças em andamento: `proposal.md`, `specs/` (deltas), `design.md`, `tasks.md` |
| `openspec/changes/archive/` | Mudanças concluídas e arquivadas |
| `docs/specs/001-assistencia-tech-v1/` | Registro histórico da versão 1.0, anterior à adoção da CLI (mantido apenas como histórico) |

## Especificações vigentes

- `design-system` — consistência visual, elementos interativos e feedback de estado.
- `responsive-interface` — adaptação a telas, navegação e formulários em telas pequenas.

## Mudanças

- `redesign-interface` — arquivada em 2026-10-29. Observação: foi arquivada com parte das tarefas de verificação manual ainda abertas (revisão completa de rotas e tamanhos de tela). Essas verificações foram incorporadas aos grupos de verificação das mudanças seguintes.
- `integrate-xano-backend` — grupos 1 a 5 concluídos (camada de dados, modo demonstração, cliente Xano); grupo 6 (contratos reais) bloqueado até a documentação oficial da API.
- `expand-service-domain` — concluída: domínio de clientes, equipamentos e ordens.
- `add-auth-and-access-control` — concluída: autenticação, perfis, permissões e portal.
- `refine-frontend-experience` — 10 de 12 tarefas: responsividade, gráficos e usabilidade (2 verificações visuais de acessibilidade pendentes).
- `add-admin-and-reports` — concluída: colaboradores, relatórios e CSV.
- `prepare-academic-delivery` — documentação de arquitetura, roteiro de demonstração e relatório técnico.

As mudanças concluídas ainda não foram arquivadas; o arquivamento incorpora os deltas às especificações vigentes e será feito após a revisão.

## Fluxo de trabalho adotado

1. **Propor** (`proposal.md`): problema, motivação, escopo e o que está fora do escopo.
2. **Especificar** (`specs/**/spec.md`): requisitos com `SHALL/MUST` e cenários `WHEN/THEN` testáveis.
3. **Projetar** (`design.md`): decisões técnicas, alternativas consideradas e riscos.
4. **Planejar** (`tasks.md`): tarefas pequenas, cada uma com sua forma de verificação.
5. **Implementar** tarefa a tarefa, marcando apenas o que foi implementado **e** verificado.
6. **Validar** com `pytest`, `openspec validate <mudança> --strict` e verificação no navegador.
7. **Arquivar** com `openspec archive <mudança>`, que incorpora os deltas às especificações vigentes.

## Comandos úteis

```powershell
openspec list                      # mudanças em andamento
openspec list --specs              # especificações vigentes
openspec status --change integrate-xano-backend
openspec validate --all --strict
```

## Rastreabilidade

Os requisitos funcionais e não funcionais gerais (`RFxx`, `RNFxx`) estão em `docs/REQUIREMENTS.md`. Os requisitos detalhados e seus cenários ficam nas especificações do OpenSpec. Uma tarefa só é marcada como concluída quando há evidência compatível (teste executado, comando validado ou verificação registrada); a existência do código, isoladamente, não prova que uma tela foi validada ou que uma integração real funciona.
