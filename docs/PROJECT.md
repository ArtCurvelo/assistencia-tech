# Assistência TECH — contexto do projeto

## Objetivo
Aplicação acadêmica de gestão de assistência técnica em Python/Reflex: atendimento, equipamentos, ordens de serviço, portal do cliente, equipe e relatórios, preservando a identidade visual dos HTMLs originais. Visão técnica em `ARCHITECTURE.md` e relatório em `ACADEMIC_REPORT.md`.

## Referências recebidas
- `base.html`: marca, navegação, rodapé e fonte Inter.
- `index.html`: página inicial, serviços, indicadores e consulta de OS.
- `login.html` e `cadastro.html`: formulários de acesso.
- `servicos.html`: lista de serviços técnicos.
- CSS enviado na conversa: fundo `#030b16`, cards `#081a2f`, verde `#39ff5a`, azul `#087cff`, fonte Inter e layouts responsivos.

## Limite explícito
A fonte de dados padrão é o modo demonstração (dados fictícios em memória, sempre identificados como tal). A integração com o Xano está preparada, mas nenhum contrato da API foi fornecido; por isso nenhum endpoint foi inventado, e as operações no modo Xano informam que a integração está pendente.

## Processo de especificação

O projeto utiliza a ferramenta OpenSpec para organizar as mudanças. Consulte `OPEN_SPEC_APPROACH.md` para o fluxo adotado e a localização dos artefatos em `openspec/`. A pasta `specs/001-assistencia-tech-v1/` é o registro histórico da versão 1.0, anterior à adoção da CLI.
