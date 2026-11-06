# Tasks

## 1. Estrutura e configuração

- [ ] 1.1 Criar os pacotes `config.py`, `models/` e `data/` (com `demo/` e `xano/`) conforme o design; verificar importando cada módulo com `python -c` na `.venv`.
- [ ] 1.2 Implementar a leitura de `ASSISTENCIA_DATA_SOURCE`, `XANO_BASE_URL` e `XANO_TIMEOUT_SECONDS` com padrões e erro para valor desconhecido; verificar com testes de configuração em `tests/test_config.py`.
- [ ] 1.3 Criar `.env.example` apenas com nomes de variáveis e valores fictícios e garantir `.env` no `.gitignore`; verificar com `git check-ignore .env` e inspeção do arquivo.

## 2. Modelos e erros

- [ ] 2.1 Criar modelos Pydantic de cliente, equipamento e ordem de serviço com campos obrigatórios validados; verificar com testes de criação válida e inválida em `tests/test_models.py`.
- [ ] 2.2 Criar a hierarquia `DataAccessError` com mensagens ao usuário em português; verificar com testes de que nenhuma `user_message` contém detalhes técnicos.

## 3. Interfaces e modo demonstração

- [ ] 3.1 Definir os `Protocol` de repositórios e o `DataGateway`; verificar que o adaptador de demonstração satisfaz as interfaces em teste.
- [ ] 3.2 Implementar o adaptador de demonstração a partir de `services/demo_data.py` (listar, buscar, cadastrar, atualizar status); verificar com testes de contrato interno em `tests/test_demo_gateway.py`.
- [ ] 3.3 Corrigir a geração de códigos para `OS-AAAA-NNNNN` sequencial; verificar com teste em que a ordem seguinte a `OS-2026-00125` recebe `OS-2026-00126`.
- [ ] 3.4 Rejeitar status fora do conjunto permitido com `ValidationError`; verificar com teste dedicado.

## 4. Estado Reflex e interface

- [ ] 4.1 Implementar `factory.get_gateway()` conforme a configuração, sem recorrer à demonstração quando `xano` estiver incompleto; verificar com testes de fábrica.
- [ ] 4.2 Migrar o `AppState` para usar o gateway em consultas e cadastros, com carregamento em `on_load`; verificar que `python -c "import assistencia_tech.assistencia_tech"` importa sem erros e que os testes existentes continuam passando.
- [ ] 4.3 Adicionar `is_loading`, mensagens de sucesso e erro (incluindo campos obrigatórios ausentes) e bloqueio de envio duplicado; verificar no navegador cadastrando com e sem campos obrigatórios.
- [ ] 4.4 Exibir a fonte de dados ativa no topo da área administrativa; verificar no navegador que o modo demonstração aparece em todas as páginas administrativas.
- [ ] 4.5 Validar no navegador (`reflex run`) consulta de OS, cadastros, buscas e mudança de status em todas as rotas, registrando o resultado neste arquivo.

## 5. Cliente HTTP do Xano

- [ ] 5.1 Implementar o cliente `httpx.AsyncClient` com endereço base e tempo limite configuráveis; verificar com testes usando `httpx.MockTransport`.
- [ ] 5.2 Implementar a tradução de status HTTP e falhas de rede para a hierarquia de erros; verificar com testes cobrindo 400, 401, 403, 404, 422, 429, 500, timeout e falha de conexão.
- [ ] 5.3 Implementar o registro de contratos vazio e o adaptador Xano que lança `ContractPendingError` sem enviar requisições; verificar com teste em que o transporte simulado não recebe nenhuma chamada.
- [ ] 5.4 Documentar em `docs/XANO_INTEGRATION.md` a arquitetura, as variáveis e o procedimento para registrar um contrato; verificar seguindo o documento para configurar o modo `xano` e observar a mensagem de integração pendente.

## 6. Contratos reais do Xano (BLOQUEADO — aguarda documentação oficial)

- [ ] 6.1 Registrar, a partir da documentação oficial, os contratos de clientes, equipamentos e ordens; verificar conferindo cada entrada com a fonte documentada.
- [ ] 6.2 Implementar o mapeamento entre as respostas documentadas e os modelos internos; verificar com testes usando exemplos de resposta extraídos da documentação.
- [ ] 6.3 Definir e implementar a autenticação conforme o contrato oficial; verificar com testes simulados e uma chamada real em ambiente de teste.
- [ ] 6.4 Executar os fluxos da interface contra o workspace Xano de teste; verificar registrando resultados neste arquivo.

## 7. Verificação integrada

- [ ] 7.1 Executar `pytest` na `.venv` e registrar o resultado neste arquivo.
- [ ] 7.2 Executar `openspec validate integrate-xano-backend --strict` e registrar o resultado.
- [ ] 7.3 Confirmar que nenhum arquivo Python ultrapassa 1000 linhas e que não há credenciais versionadas; verificar com contagem de linhas e busca no repositório.

## Workflow follow-up

- Arquivar a mudança com o fluxo oficial do OpenSpec somente após concluir o grupo 6, ou dividir o grupo 6 em uma mudança própria caso a documentação do Xano demore, mediante decisão registrada.
