# Design 001 — Plano de implementação

## Estrutura

- `assistencia_tech/assistencia_tech.py`: composição das páginas e registro das rotas.
- `assistencia_tech/components.py`: componentes visuais reutilizáveis.
- `assistencia_tech/state.py`: estado reativo e handlers.
- `assistencia_tech/services/demo_data.py`: dados iniciais fictícios.
- `assets/style.css`: estilos e breakpoints.
- `tests/`: testes unitários básicos.
- `docs/`: documentação de projeto e especificação.

## Decisões técnicas

1. Usar Reflex para construir a UI em Python.
2. Separar os dados fictícios do estado e da composição visual.
3. Não acoplar a interface diretamente a um banco inexistente no contrato atual.
4. Exibir mensagens explícitas onde autenticação e persistência ainda não existem.
5. Manter a identidade visual escura com detalhes verdes e azuis do CSS recebido.

## Riscos e mitigação

- **Diferenças de API entre versões do Reflex:** instalar dependências em ambiente virtual e validar o comando de inicialização.
- **Estado em memória:** comunicar que os registros são temporários e não persistem após reinicialização.
- **Contratos de API desconhecidos:** aguardar documentação ou exemplos reais antes de implementar integração.
- **Compatibilidade de componentes dinâmicos:** validar as páginas no runtime Reflex e adicionar testes de interação.

## Integração futura

A camada `services` deve evoluir para clientes de API/repositórios quando os contratos reais estiverem disponíveis. Credenciais devem ser fornecidas por variáveis de ambiente e nunca versionadas no repositório.
