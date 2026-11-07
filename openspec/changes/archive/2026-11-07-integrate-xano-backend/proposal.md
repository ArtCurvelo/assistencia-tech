# Proposal: Integração do backend Xano

## Why

Hoje toda a lógica de dados do Assistência TECH vive dentro do estado da interface (`AppState`), com listas fictícias carregadas diretamente. Isso impede a integração com o Xano, mistura apresentação com acesso a dados e torna o comportamento difícil de testar. É preciso criar agora uma fronteira de acesso a dados, para que as próximas funcionalidades (domínio completo, autenticação, administração) já nasçam desacopladas do backend e para que a integração real possa ser ligada assim que os contratos oficiais do Xano forem fornecidos.

## What Changes

- Criar uma camada de acesso a dados com interfaces internas para clientes, equipamentos e ordens de serviço, separada dos componentes visuais.
- Implementar um **modo demonstração** (dados em memória) atrás dessas interfaces, preservando os registros e os fluxos atuais.
- Selecionar a fonte de dados por configuração (variáveis de ambiente), sem credenciais no código e com um arquivo `.env.example` documentado.
- Exibir na interface qual fonte de dados está ativa; o modo demonstração permanece sempre identificado.
- Padronizar erros de acesso a dados e traduzi-los em mensagens compreensíveis, com estados de carregamento, sucesso e erro nas operações.
- Corrigir a geração do código das ordens de serviço, que hoje produz formatos inconsistentes (`OS-2026-126` ao lado de `OS-2026-00125`).
- Preparar o cliente HTTP do Xano (configuração, tempo limite, tratamento de falhas) testado com respostas simuladas.
- Implementar as operações reais no Xano **somente** depois de receber a documentação oficial; até lá, operações sem contrato documentado falham de forma explícita.

## Capabilities

### New Capabilities

- `data-source`: seleção da fonte de dados, modo demonstração, identificação da fonte ativa e comunicação de falhas de acesso a dados ao usuário.
- `backend-integration`: comunicação com o backend Xano — configuração, limites de tempo, tradução de falhas e a regra de só operar contratos documentados.

### Modified Capabilities

- Nenhuma. As capacidades `design-system` e `responsive-interface` não têm requisitos alterados.

## Impact

- **Código:** `assistencia_tech/state.py` passa a depender da camada de dados; novos pacotes para configuração, modelos, repositórios e cliente Xano; `services/demo_data.py` passa a alimentar o modo demonstração.
- **Dependências:** `httpx` (já presente como dependência do Reflex) declarada explicitamente em `requirements.txt`; `pytest` em `requirements-dev.txt`.
- **Configuração:** novas variáveis de ambiente documentadas em `.env.example`.
- **Testes:** testes unitários de configuração, modelos, modo demonstração e cliente Xano com transporte simulado.

## Out of Scope

- Novos campos e entidades de domínio (diagnóstico, peças, pagamentos, histórico) — mudança própria posterior.
- Autenticação, perfis e proteção de rotas — mudança própria posterior.
- Reformulação visual das páginas além dos estados de carregamento, erro e indicador de fonte.
- Qualquer endpoint, método HTTP, campo ou fluxo de autenticação do Xano que não esteja na documentação oficial fornecida.
- Persistência local (SQLite ou arquivos) como substituta do Xano.
