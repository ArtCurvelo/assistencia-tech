# backend-integration Specification

## Purpose
Define as regras de comunicação entre o Assistência TECH e o backend Xano, incluindo configuração segura, limites de tempo, tratamento de falhas e a obrigação de operar apenas contratos de API documentados oficialmente.

## Requirements

### Requirement: Configuração externa e segura

O endereço base da API, o tempo limite e quaisquer credenciais do Xano SHALL ser fornecidos por configuração do ambiente. Credenciais MUST NOT constar no código-fonte nem no repositório, e o projeto SHALL documentar as variáveis esperadas em um arquivo de exemplo sem valores reais.

#### Scenario: Repositório sem credenciais
- **WHEN** o código-fonte e os arquivos versionados são inspecionados
- **THEN** nenhum token, senha ou chave do Xano é encontrado, e o arquivo de exemplo contém apenas nomes de variáveis e valores fictícios

### Requirement: Somente contratos documentados

O sistema SHALL executar no Xano apenas operações cujo endpoint, método, parâmetros e formato de resposta estejam registrados a partir da documentação oficial. Uma operação sem contrato registrado MUST falhar de forma explícita, informando que a integração está pendente.

#### Scenario: Operação sem contrato documentado
- **WHEN** a fonte Xano está ativa e o usuário aciona uma operação cujo contrato ainda não foi registrado
- **THEN** nenhuma requisição é enviada e o usuário é informado de que essa funcionalidade ainda não está integrada ao backend

### Requirement: Tempo limite das requisições

Toda requisição ao Xano SHALL respeitar um tempo limite configurável, com valor padrão definido, e uma requisição que exceder esse tempo SHALL ser tratada como serviço indisponível.

#### Scenario: Backend lento
- **WHEN** o backend não responde dentro do tempo limite configurado
- **THEN** a operação é interrompida e tratada como serviço indisponível

### Requirement: Tradução das respostas de erro

O sistema SHALL classificar as falhas de comunicação com o Xano em categorias compreensíveis — dados inválidos, não autorizado, não encontrado, serviço indisponível e erro inesperado — com base no código de status HTTP da resposta.

#### Scenario: Recurso inexistente
- **WHEN** o backend responde que o registro solicitado não existe
- **THEN** a operação é classificada como não encontrada e o usuário recebe uma mensagem correspondente

#### Scenario: Erro interno do backend
- **WHEN** o backend responde com um erro de servidor
- **THEN** a operação é classificada como serviço indisponível, sem exibir o conteúdo técnico da resposta ao usuário

#### Scenario: Acesso negado
- **WHEN** o backend responde que a requisição não está autorizada
- **THEN** a operação é classificada como não autorizada e o usuário recebe uma mensagem correspondente
