# continuous-integration Specification

## Purpose
Define a integração contínua do Assistência TECH: verificações automáticas no GitHub Actions a cada envio ao repositório, sem segredos, incluindo as regras do projeto conferidas por testes.

## Requirements

### Requirement: Verificações automáticas a cada envio

O repositório SHALL ter um workflow do GitHub Actions que, a cada `push` e `pull_request`, instala as dependências do projeto num ambiente limpo e executa os testes automatizados, o verificador de contrato com as cópias da documentação do Xano, a montagem de todas as páginas do aplicativo e a validação estrita das especificações OpenSpec. Qualquer falha MUST deixar a execução com status de falha.

#### Scenario: Envio com um teste quebrado
- **WHEN** um commit enviado ao GitHub faz um teste falhar
- **THEN** o workflow termina com falha e indica o teste que falhou

#### Scenario: Envio correto
- **WHEN** um commit enviado ao GitHub passa em todas as verificações
- **THEN** o workflow termina com sucesso

### Requirement: Integração contínua sem segredos

O workflow MUST NOT usar credenciais, tokens ou o Xano real; os testes SHALL usar o modo demonstração, servidores simulados e as cópias versionadas da documentação da API.

#### Scenario: Repositório sem segredos configurados
- **WHEN** o workflow roda num repositório sem nenhum segredo configurado
- **THEN** todas as verificações executam normalmente

### Requirement: Regras do projeto verificadas automaticamente

Os testes SHALL falhar quando um arquivo Python versionado tiver 1.000 linhas ou mais, quando um arquivo `.env` estiver versionado ou quando um arquivo versionado contiver um token JWT.

#### Scenario: Arquivo grande demais
- **WHEN** um arquivo Python versionado passa a ter 1.000 linhas
- **THEN** o teste de regras do projeto falha citando o arquivo
