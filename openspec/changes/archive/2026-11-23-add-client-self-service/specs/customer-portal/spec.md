# Spec Delta

## ADDED Requirements

### Requirement: Equipamentos do cliente no portal

O portal SHALL permitir que o cliente cadastre equipamentos (tipo, marca, modelo, número de série opcional e observações) e liste os próprios equipamentos. O cliente MUST NOT ver nem cadastrar equipamentos de outro cliente, e um número de série já cadastrado MUST ser recusado.

#### Scenario: Cadastro de equipamento
- **WHEN** a cliente cadastra um Notebook Dell Inspiron no portal
- **THEN** o equipamento aparece em "Meus equipamentos" e pode ser escolhido numa solicitação

#### Scenario: Número de série repetido
- **WHEN** a cliente informa um número de série que já existe
- **THEN** o cadastro é recusado com a mensagem de número de série já cadastrado

### Requirement: Solicitação de atendimento pelo cliente

O portal SHALL permitir que o cliente solicite atendimento para um equipamento próprio, descrevendo o problema e escolhendo a forma de entrega: levar à loja ou coleta por motoboy. Na coleta, o endereço e o período de preferência SHALL ser obrigatórios. Ao escolher levar à loja, o portal SHALL exibir o endereço e o horário configurados da assistência. A solicitação SHALL criar uma ordem no status Solicitado, visível para a equipe.

#### Scenario: Levar à loja
- **WHEN** a cliente solicita atendimento escolhendo "Levar à loja"
- **THEN** a ordem é criada em Solicitado e o portal mostra o endereço da assistência

#### Scenario: Coleta sem endereço
- **WHEN** a cliente escolhe "Coleta por motoboy" e não informa o endereço
- **THEN** a solicitação é recusada com a mensagem para informar o endereço de coleta

#### Scenario: Equipamento de outro cliente
- **WHEN** um cliente tenta solicitar atendimento para um equipamento que não é dele
- **THEN** a solicitação é recusada
