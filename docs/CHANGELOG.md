# Changelog

## Não lançado — Fase 1 (camada de dados, mudança `integrate-xano-backend`)
- Camada de acesso a dados com interfaces internas (`DataGateway`) e modo demonstração em memória.
- Seleção da fonte de dados por variáveis de ambiente (`.env.example`); modo Xano nunca recorre aos dados fictícios.
- Modelos Pydantic com validação e mensagens em português; hierarquia de erros com mensagens seguras ao usuário.
- Cliente HTTP do Xano com tempo limite e tradução de status HTTP; registro de contratos vazio até a documentação oficial.
- Interface: selo da fonte de dados ativa, alerta de falha de carregamento, mensagens e toasts de sucesso/erro, botões com estado de carregamento, estados vazios no painel e em equipamentos.
- Correções: código de OS agora sempre `OS-AAAA-NNNNN` (antes gerava `OS-2026-126`); card "Ordens em andamento" exibia o nome interno da variável; formulários inválidos não davam retorno ao usuário.
- 53 novos testes automatizados (56 no total).

## Não lançado — Fase 0 (fundação)
- Repositório git inicializado com snapshot do estado anterior.
- Versão do Reflex alinhada à `.venv` (0.8.28); `httpx` declarado; `pytest` em `requirements-dev.txt`.
- OpenSpec: spec `design-system` renomeada para `spec.md` e convertida ao formato de especificação vigente; spec `responsive-interface` sincronizada a partir da mudança arquivada; contexto do projeto definido em `openspec/config.yaml`.
- Mudança `integrate-xano-backend` planejada (proposta, specs, design e tarefas) e validada com `--strict`.
- Documentação corrigida: o projeto utiliza a CLI OpenSpec; referências do README a arquivos inexistentes removidas.

## 1.0.0 — protótipo demonstrativo
- Reconstruídas as páginas públicas de início, serviços, login e cadastro em Reflex.
- Criado painel administrativo com visão geral, clientes, equipamentos e ordens de serviço.
- Adicionada consulta demonstrativa de OS, busca e atualização de status.
- Preservada a paleta visual original.
- Documentadas limitações de autenticação, persistência e APIs.
