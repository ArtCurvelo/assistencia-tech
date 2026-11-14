# Spec Delta

## ADDED Requirements

### Requirement: Site mantido acordado

O repositório SHALL ter um workflow agendado que acessa o endereço público `/ping` do site a cada 10 minutos, de segunda a sexta em horário comercial, para evitar a espera do plano gratuito, e que também pode ser disparado manualmente. O workflow MUST NOT usar segredos.

#### Scenario: Apresentação em horário comercial
- **WHEN** o site fica 30 minutos sem visitas numa tarde de dia útil
- **THEN** o workflow o acessou nesse intervalo e a próxima visita não espera o site acordar
