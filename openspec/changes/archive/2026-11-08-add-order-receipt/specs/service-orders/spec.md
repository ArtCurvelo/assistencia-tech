# Spec Delta

## ADDED Requirements

### Requirement: Consulta pública por link

O sistema SHALL oferecer a página pública `/consulta/<código>`, que abre a consulta da ordem já preenchida e exibe os mesmos dados limitados da consulta pública. Códigos fora do formato `OS-AAAA-NNNNN` MUST receber a mensagem de código não encontrado sem consulta ao backend.

#### Scenario: QR code lido pelo celular
- **WHEN** o cliente abre `/consulta/OS-2026-00125`
- **THEN** a página mostra o status, o equipamento, a previsão de entrega e a última atualização da ordem, sem dados pessoais nem valores

#### Scenario: Código inválido no link
- **WHEN** alguém abre `/consulta/qualquer-coisa`
- **THEN** a página informa que o código não foi encontrado
