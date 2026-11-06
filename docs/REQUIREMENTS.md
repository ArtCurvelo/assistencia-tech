# Requisitos

Visão geral rastreável dos requisitos. O comportamento detalhado, com cenários verificáveis, está nas especificações do OpenSpec indicadas na coluna "Spec".

## Requisitos funcionais

| ID | Requisito | Spec |
|---|---|---|
| RF01 | Exibir página inicial com a identidade visual Assistência TECH | `design-system` |
| RF02 | Listar os serviços oferecidos | `design-system` |
| RF03 | Apresentar formulários demonstrativos de login e cadastro | — (autenticação real em mudança futura) |
| RF04 | Consultar publicamente uma OS pelo código, sem expor dados pessoais | `service-orders` |
| RF05 | Exibir painel com indicadores (abertas, aguardando aprovação, prontas, valor a receber) e ordens recentes | `service-orders` |
| RF06 | Cadastrar clientes com CPF, e-mail e telefone validados e únicos | `client-management` |
| RF07 | Pesquisar clientes por nome, e-mail, CPF ou telefone | `client-management` |
| RF08 | Editar clientes e excluí-los com confirmação, bloqueando quando houver vínculos | `client-management` |
| RF09 | Exibir o histórico de atendimentos de cada cliente | `client-management` |
| RF10 | Cadastrar equipamentos vinculados a clientes, com número de série único opcional | `equipment-management` |
| RF11 | Filtrar e pesquisar equipamentos; editar e excluir com regras de vínculo | `equipment-management` |
| RF12 | Exibir o histórico de manutenção de cada equipamento | `equipment-management` |
| RF13 | Abrir OS para um equipamento do cliente, com código único `OS-AAAA-NNNNN` | `service-orders`, `data-source` |
| RF14 | Controlar o status da OS com transições e pré-condições definidas | `service-orders` |
| RF15 | Atribuir técnico responsável e registrar diagnóstico | `service-orders` |
| RF16 | Montar orçamento com serviços e peças e calcular valores | `service-orders` |
| RF17 | Registrar pagamentos e condicionar a entrega à quitação | `service-orders` |
| RF18 | Registrar histórico imutável de alterações da OS | `service-orders` |
| RF19 | Filtrar ordens por status e técnico e pesquisar por código, cliente ou equipamento | `service-orders` |
| RF20 | Selecionar a fonte de dados (demonstração ou Xano) por configuração, identificando a fonte ativa | `data-source` |

## Requisitos não funcionais

| ID | Requisito | Spec / evidência |
|---|---|---|
| RNF01 | Usar Python com Reflex 0.8 | `requirements.txt` |
| RNF02 | Preservar a identidade visual escura com verde e azul | `design-system` |
| RNF03 | Adaptar o layout a telas menores | `responsive-interface` |
| RNF04 | Manter arquivos Python com menos de 1000 linhas (meta: 400) | contagem registrada nas tarefas |
| RNF05 | Identificar claramente o caráter demonstrativo dos dados | `data-source` |
| RNF06 | Não afirmar persistência ou autenticação reais | `data-source` |
| RNF07 | Nunca inventar contratos da API do Xano; operações sem contrato falham de forma explícita | `backend-integration` |
| RNF08 | Não versionar credenciais; configuração por variáveis de ambiente | `backend-integration` |
| RNF09 | Mensagens de erro compreensíveis, sem detalhes técnicos | `data-source`, `design-system` |
| RNF10 | Regras de negócio isoladas em funções puras e cobertas por testes automatizados | `tests/` |
| RNF11 | Valores monetários com `Decimal`, sem `float` | `domain/validators.py` |

## Critérios de aceitação gerais

- Cada cenário das specs tem um teste automatizado correspondente ou uma verificação registrada no `tasks.md` da mudança.
- `pytest` e `openspec validate --all --strict` passam.
- Os fluxos principais foram percorridos no navegador nos modos demonstração e Xano sem contratos.
