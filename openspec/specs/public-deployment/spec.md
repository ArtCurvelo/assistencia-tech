# public-deployment Specification

## Purpose
Define a publicação do Assistência TECH num endereço público HTTPS, com o backend Xano real, construída a partir do repositório no GitHub e sem credenciais versionadas.

## Requirements

### Requirement: Site publicado com o backend real

O sistema SHALL ficar disponível num endereço público HTTPS, usando o backend Xano como fonte de dados, com as mesmas páginas, regras e permissões do ambiente de desenvolvimento. O repositório MUST NOT conter credenciais para isso.

#### Scenario: Acesso pelo professor
- **WHEN** o professor abre o endereço público do site
- **THEN** a página inicial é exibida e o login funciona com as contas do Xano

#### Scenario: Atualização a partir do GitHub
- **WHEN** um commit é enviado ao ramo `main`
- **THEN** a hospedagem constrói e publica a nova versão

### Requirement: Endereço público no aplicativo

Quando publicado, o aplicativo SHALL usar o endereço público como endereço da API do frontend e o QR code dos comprovantes SHALL apontar para `<endereço público>/consulta/<código>`.

#### Scenario: QR code no site publicado
- **WHEN** a atendente abre o comprovante de uma ordem no site publicado
- **THEN** o endereço do QR code começa com o endereço público do site

### Requirement: Sem telemetria do framework

O aplicativo publicado MUST NOT enviar telemetria de uso do Reflex.

#### Scenario: Configuração de produção
- **WHEN** o aplicativo é iniciado
- **THEN** a configuração do Reflex tem a telemetria desligada

### Requirement: Site mantido acordado

O repositório SHALL ter um workflow agendado que acessa o endereço público `/ping` do site a cada 10 minutos, de segunda a sexta em horário comercial, para evitar a espera do plano gratuito, e que também pode ser disparado manualmente. O workflow MUST NOT usar segredos.

#### Scenario: Apresentação em horário comercial
- **WHEN** o site fica 30 minutos sem visitas numa tarde de dia útil
- **THEN** o workflow o acessou nesse intervalo e a próxima visita não espera o site acordar
