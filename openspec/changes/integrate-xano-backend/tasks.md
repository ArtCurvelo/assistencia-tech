# Tasks

## 1. Estrutura e configuração

- [x] 1.1 Criar os pacotes `config.py`, `models/` e `data/` (com `demo/` e `xano/`) conforme o design; verificar importando cada módulo com `python -c` na `.venv`.
- [x] 1.2 Implementar a leitura de `ASSISTENCIA_DATA_SOURCE`, `XANO_BASE_URL` e `XANO_TIMEOUT_SECONDS` com padrões e erro para valor desconhecido; verificar com testes de configuração em `tests/test_config.py`.
- [x] 1.3 Criar `.env.example` apenas com nomes de variáveis e valores fictícios e garantir `.env` no `.gitignore`; verificar com `git check-ignore .env` e inspeção do arquivo.

## 2. Modelos e erros

- [x] 2.1 Criar modelos Pydantic de cliente, equipamento e ordem de serviço com campos obrigatórios validados; verificar com testes de criação válida e inválida em `tests/test_models.py`.
- [x] 2.2 Criar a hierarquia `DataAccessError` com mensagens ao usuário em português; verificar com testes de que nenhuma `user_message` contém detalhes técnicos.

## 3. Interfaces e modo demonstração

- [x] 3.1 Definir os `Protocol` de repositórios e o `DataGateway`; verificar que o adaptador de demonstração satisfaz as interfaces em teste.
- [x] 3.2 Implementar o adaptador de demonstração a partir de `services/demo_data.py` (listar, buscar, cadastrar, atualizar status); verificar com testes de contrato interno em `tests/test_demo_gateway.py`.
- [x] 3.3 Corrigir a geração de códigos para `OS-AAAA-NNNNN` sequencial; verificar com teste em que a ordem seguinte a `OS-2026-00125` recebe `OS-2026-00126`.
- [x] 3.4 Rejeitar status fora do conjunto permitido com `ValidationError`; verificar com teste dedicado.

## 4. Estado Reflex e interface

- [x] 4.1 Implementar `factory.get_gateway()` conforme a configuração, sem recorrer à demonstração quando `xano` estiver incompleto; verificar com testes de fábrica.
- [x] 4.2 Migrar o `AppState` para usar o gateway em consultas e cadastros, com carregamento em `on_load`; verificar que `python -c "import assistencia_tech.assistencia_tech"` importa sem erros e que os testes existentes continuam passando.
- [x] 4.3 Adicionar `is_loading`, mensagens de sucesso e erro (incluindo campos obrigatórios ausentes) e bloqueio de envio duplicado; verificar no navegador cadastrando com e sem campos obrigatórios.
- [x] 4.4 Exibir a fonte de dados ativa no topo da área administrativa; verificar no navegador que o modo demonstração aparece em todas as páginas administrativas.
- [x] 4.5 Validar no navegador (`reflex run`) consulta de OS, cadastros, buscas e mudança de status em todas as rotas, registrando o resultado neste arquivo.

## 5. Cliente HTTP do Xano

- [x] 5.1 Implementar o cliente `httpx.AsyncClient` com endereço base e tempo limite configuráveis; verificar com testes usando `httpx.MockTransport`.
- [x] 5.2 Implementar a tradução de status HTTP e falhas de rede para a hierarquia de erros; verificar com testes cobrindo 400, 401, 403, 404, 422, 429, 500, timeout e falha de conexão.
- [x] 5.3 Implementar o registro de contratos vazio e o adaptador Xano que lança `ContractPendingError` sem enviar requisições; verificar com teste em que o transporte simulado não recebe nenhuma chamada.
- [x] 5.4 Documentar em `docs/XANO_INTEGRATION.md` a arquitetura, as variáveis e o procedimento para registrar um contrato; verificar seguindo o documento para configurar o modo `xano` e observar a mensagem de integração pendente.

## 6. Contratos reais do Xano (opção A: ajustar o Xano ao contrato-alvo)

- [x] 6.0 Obter a documentação OpenAPI dos grupos e analisar a compatibilidade; verificado com as cópias em `docs/xano-openapi/` e a análise em `docs/XANO_CONTRACT_ANALYSIS.md` (grupo Sistema de Gestão: HTTP 403).
- [x] 6.0a Definir o contrato-alvo (`docs/XANO_BACKEND_SPEC.md`, `tools/xano_target_contract.py`) e o verificador `tools/xano_contract_check.py`; verificado com `tests/test_xano_contract_check.py` (6 testes) e a execução online: 1 de 27 endpoints atendidos em 07/11/2026.
- [x] 6.0b Usar o repositório de certificados do sistema no cliente Xano (`truststore`); verificado baixando a documentação com verificação TLS ativa.
- [x] 6.1 Obter `OK` nos 27 endpoints do verificador; verificar executando `python -m tools.xano_contract_check` e registrando a saída. (Backend próprio em XanoScript no workspace 170741, grupos `assistencia-tech-auth`, `-cliente` e `-os`: 27 de 27 em 07/11/2026.)
- [x] 6.2 Registrar em `CONTRACTS` cada operação interna com o endpoint documentado e implementar o mapeamento das respostas para os modelos internos; verificar com testes usando os esquemas da documentação. (28 contratos; `tests/test_xano.py` e `tests/test_xano_repositories.py`.)
- [x] 6.3 Implementar a sessão com o JWT do Xano (D12) e os perfis vindos de `GET /auth/me`; verificar com testes simulados e um login real no workspace. (Login real do administrador e da cliente de teste em 07/11/2026; o JWT fica na sessão do servidor.)
- [x] 6.4 Implementar o agregado da OS sobre `os_servicos`, `os_itens`, `pagamentos` e `os_historico` (D13), a consulta pública e o portal (D14); verificar com testes simulados. (`data/xano/orders.py`; o portal usa `GET /portal/minha_conta` e o *addon* `_aparelho`, acrescentados ao contrato-alvo e enviados ao Xano; verificador: 28 de 28 em 07/11/2026.)
- [x] 6.5 Executar no navegador, com `ASSISTENCIA_DATA_SOURCE=xano`, o roteiro de `docs/DEMO_SCRIPT.md` contra o workspace e registrar os resultados neste arquivo.
  - Parcial (07/11/2026, `reflex-xano` em `.claude/launch.json`): consulta pública com código inexistente → "Código não encontrado" (resposta real do Xano); login com conta inexistente → "E-mail ou senha inválidos."; sem acesso rápido às contas de demonstração. Corrigido o selo da página inicial, que dizia "dados fictícios" também no modo Xano. Falta o roteiro completo, que depende do primeiro administrador e do envio de `GET /portal/minha_conta`.
  - Completo (07/11/2026, administrador real no Chrome; cliente de teste no navegador do app). Registros de teste no Xano: Paula Atendente (teste), Carlos Mendes (teste, técnico), Joana Teixeira (cliente), Notebook Dell Inspiron 15 e **OS-2026-00001**. Senhas de teste geradas aleatoriamente e mantidas fora do repositório.
    - Cadastro público da cliente → cliente e conta criados juntos; portal com CPF mascarado.
    - Colaboradores e equipamento cadastrados pelo administrador; técnico listado por `GET /tecnicos`.
    - OS aberta; "Em análise" sem técnico → recusada; técnico atribuído → "Em análise".
    - "Aguardando aprovação" sem diagnóstico → "Registre o diagnóstico técnico antes de enviar para aprovação."
    - Diagnóstico, serviço R$ 150,00 e peça R$ 180,00 → aprovação → "Em reparo" → "Concluído".
    - "Entregue" com saldo → "Há saldo a receber de R$ 330,00."; pagamentos de R$ 130,00 (PIX) e R$ 200,00 (crédito) → "Pago" → "Entregue", sem próximos status.
    - Consulta pública → somente código, status, aparelho e data.
    - Portal da cliente → orçamento, pagamentos e andamento sem autores internos; `/admin/clientes` → "Acesso negado"; o Xano recusa o token da cliente em `cliente`, `os_servicos` e `usuarios` (403).
  - Defeitos encontrados e corrigidos durante a execução:
    - Limite do plano gratuito do Xano (10 requisições a cada 20 s) derrubava a sessão → cache curto de leituras, ritmo de requisições e indisponibilidade sem logout (`data/xano/limits.py`).
    - Listagens sem paginação usavam `as: "items._itens"` nos *addons* e chegavam sem itens, pagamentos e aparelho → `as: "_itens"` em `GET /os_servicos` e `GET /portal/minhas_ordens`; teste estático `tests/test_xanoscript_static.py`.
  - Observações: cada edição de arquivo do projeto reinicia o backend do Reflex em desenvolvimento e encerra as sessões em memória; a data do pagamento é só a data (exibida com 00:00).

## 7. Verificação integrada

- [x] 7.1 Executar `pytest` na `.venv` e registrar o resultado neste arquivo.
- [x] 7.2 Executar `openspec validate integrate-xano-backend --strict` e registrar o resultado.
- [x] 7.3 Confirmar que nenhum arquivo Python ultrapassa 1000 linhas e que não há credenciais versionadas; verificar com contagem de linhas e busca no repositório.

## Registro de verificação (2026-11-06)

- **pytest (.venv):** 56 testes aprovados, 0 falhas (`test_config`, `test_models`, `test_demo_gateway`, `test_factory`, `test_xano`, `test_demo_data`).
- **OpenSpec:** `openspec validate integrate-xano-backend --strict` válido.
- **Tamanho dos arquivos:** maior arquivo Python com 357 linhas (`assistencia_tech.py`).
- **Credenciais:** busca por chaves/tokens/senhas sem ocorrências no código; `.env` ignorado (`git check-ignore .env`).
- **Navegador — modo demonstração (`reflex run`):**
  - `/admin`: indicadores 3/2/3/3, ordens recentes e selo "Modo demonstração". Corrigido erro pré-existente em que o card "Ordens em andamento" exibia o nome interno da variável.
  - `/admin/clientes`: cadastro válido com mensagem e toast de sucesso; e-mail duplicado com mensagem de erro; nome só com espaços → "Preencha o campo obrigatório: Nome." sem criar registro; busca por "rafael" filtra para 1 linha.
  - `/admin/equipamentos`: cadastro de equipamento para cliente existente com mensagem de sucesso.
  - `/admin/ordens`: nova ordem gerada como `OS-2026-00126`; status alterado para "Em análise" com mensagem de sucesso.
  - `/`: consulta de `os-2026-00126` retorna o status (consulta demonstrativa); `OS-1999-00001` → código não encontrado.
  - Os registros criados em uma página aparecem nas demais (gateway único por processo).
- **Navegador — modo Xano sem contratos** (`ASSISTENCIA_DATA_SOURCE=xano`, `XANO_BASE_URL` fictício): selo "Backend Xano", alerta "aguardando a documentação oficial da API", nenhum dado de demonstração exibido, tabelas com estado vazio.
- **Não verificado visualmente:** o indicador de carregamento do botão e o bloqueio de envio duplicado não puderam ser observados, porque as operações do modo demonstração terminam instantaneamente; o comportamento está implementado (`loading`/`disabled` ligados a `is_loading` e guarda em `_start`).
- **Não verificado:** caso `xano` sem `XANO_BASE_URL` no navegador (coberto por `test_factory.py`; usa o mesmo alerta da interface).

## Workflow follow-up

- Arquivar a mudança com o fluxo oficial do OpenSpec somente após concluir o grupo 6, ou dividir o grupo 6 em uma mudança própria caso a documentação do Xano demore, mediante decisão registrada.
