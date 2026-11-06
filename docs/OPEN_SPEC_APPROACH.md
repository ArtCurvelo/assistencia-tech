# Documentação de engenharia inspirada no OpenSpec

## Objetivo deste documento

Este projeto **não utiliza o OpenSpec como ferramenta ou CLI**. Em vez disso, mantém documentos versionáveis que registram intenção, requisitos, decisões de arquitetura, tarefas e evidências de validação, inspirados no fluxo de trabalho de especificação antes da implementação.

Isso deve ser descrito ao professor como **processo de especificação inspirado no OpenSpec**, e não como “OpenSpec instalado” ou “OpenSpec executado”.

## Como navegar na documentação

- `PROJECT.md`: contexto, problema e escopo.
- `REQUIREMENTS.md`: requisitos e critérios de aceitação gerais.
- `DESIGN.md`: arquitetura e decisões técnicas.
- `TASKS.md`: plano de trabalho e estado das atividades.
- `CHANGELOG.md`: mudanças relevantes por versão.
- `specs/001-assistencia-tech-v1/PROPOSAL.md`: proposta e motivação da mudança.
- `specs/001-assistencia-tech-v1/SPEC.md`: comportamento esperado e critérios verificáveis.
- `specs/001-assistencia-tech-v1/DESIGN.md`: plano de implementação.
- `specs/001-assistencia-tech-v1/TASKS.md`: tarefas rastreáveis de implementação e validação.

## Fluxo de trabalho adotado

1. **Propor:** registrar problema, motivação, escopo e não objetivos.
2. **Especificar:** definir comportamentos e critérios de aceitação antes de considerar a funcionalidade pronta.
3. **Projetar:** registrar componentes, estado, serviços, riscos e decisões.
4. **Planejar:** dividir o trabalho em tarefas pequenas e verificáveis.
5. **Implementar:** desenvolver conforme a especificação.
6. **Validar:** executar testes e registrar o que foi e o que não foi validado.
7. **Atualizar:** manter tarefas, changelog e documentação coerentes com o código.

## Rastreabilidade

Cada requisito possui um identificador (`RFxx` ou `RNFxx`) e deve apontar para uma ou mais tarefas. Uma tarefa só deve ser marcada como concluída quando houver evidência compatível. A existência do código, isoladamente, não prova que uma tela foi validada visualmente ou que uma integração real funciona.

## Limitações atuais

- A aplicação ainda é um protótipo demonstrativo.
- Os dados são fictícios e não têm persistência em banco.
- Login e cadastro não autenticam usuários.
- As APIs e seus contratos ainda não foram integrados.
- Os testes atuais cobrem a estrutura dos dados demonstrativos; não cobrem toda a interface Reflex.
- A inicialização e a renderização no navegador ainda precisam ser validadas no ambiente de desenvolvimento.

## Declaração sugerida para o relatório acadêmico

> O projeto adotou um processo de especificação e implementação inspirado nas práticas do OpenSpec, mantendo artefatos versionáveis de proposta, requisitos, design, tarefas e validação. A ferramenta OpenSpec não foi utilizada diretamente; os documentos foram mantidos no repositório para tornar as decisões e os critérios de aceite auditáveis.
