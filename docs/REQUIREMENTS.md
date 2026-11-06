# Requisitos — versão 1.0

## Requisitos funcionais
- RF01: exibir página inicial com identidade visual Assistência TECH.
- RF02: listar os serviços oferecidos.
- RF03: apresentar formulários demonstrativos de login e cadastro.
- RF04: permitir consultar uma OS presente nos dados fictícios.
- RF05: exibir painel administrativo com indicadores e ordens recentes.
- RF06: listar e cadastrar clientes durante a sessão.
- RF07: pesquisar clientes por nome/e-mail.
- RF08: listar e cadastrar equipamentos durante a sessão.
- RF09: criar ordens de serviço durante a sessão.
- RF10: filtrar ordens por código, cliente ou equipamento.
- RF11: atualizar o status de uma ordem entre Recebido, Em análise, Em reparo e Concluído.

## Requisitos não funcionais
- RNF01: usar Python com Reflex.
- RNF02: preservar a paleta e o estilo geral do CSS original.
- RNF03: adaptar layout para telas menores.
- RNF04: manter código em módulos com menos de 1000 linhas por arquivo.
- RNF05: identificar claramente o caráter demonstrativo dos dados.
- RNF06: não afirmar persistência ou autenticação real.
- RNF07: preparar camada de serviços para futura integração sem inventar contratos de API.

## Critérios de aceitação
- As rotas públicas e administrativas estão definidas no app.
- Os formulários administrativos alteram o estado demonstrativo.
- Busca de clientes e ordens filtra os registros.
- Consulta de OS diferencia código conhecido de código desconhecido.
- Testes automatizados validam estrutura básica dos dados demonstrativos.
- A documentação explica instalação, execução e limitações.
