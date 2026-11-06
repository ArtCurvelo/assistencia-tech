# Changelog

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
