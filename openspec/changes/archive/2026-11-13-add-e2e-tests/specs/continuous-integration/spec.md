# Spec Delta

## ADDED Requirements

### Requirement: Testes de ponta a ponta no navegador

A integração contínua SHALL compilar o site em modo produção, servi-lo em modo demonstração e executar, num navegador real, testes dos fluxos principais: página inicial, navegação por teclado, consulta pública, proteção de páginas, painel e quadro da equipe, comprovante e portal do cliente. Esses testes MUST NOT usar credenciais nem o Xano real.

#### Scenario: Tela quebrada
- **WHEN** um commit faz o login deixar de redirecionar para a área do usuário
- **THEN** o job de ponta a ponta falha

#### Scenario: Foco pelo teclado
- **WHEN** o teste pressiona Tab na página inicial
- **THEN** o foco vai para "Pular para o conteúdo", que fica visível
