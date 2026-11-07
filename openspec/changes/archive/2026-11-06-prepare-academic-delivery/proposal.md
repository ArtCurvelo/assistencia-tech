# Proposal: Preparação da entrega acadêmica

## Why

As funcionalidades das fases 1 a 5 estão implementadas e verificadas, mas a avaliação depende de o professor perceber rapidamente a engenharia aplicada: arquitetura, modelagem, requisitos, segurança, testes e processo. Hoje essa informação está espalhada entre specs, registros de tarefas e documentos parciais, e não existe um roteiro de demonstração reproduzível.

## What Changes

- `docs/ARCHITECTURE.md`: camadas, mapa de módulos, fluxo de uma requisição, decisões principais, segurança e estratégia de testes, com diagramas Mermaid.
- `docs/DEMO_SCRIPT.md`: roteiro de demonstração cronometrado (cerca de 15 minutos), com preparação, contas, passos, o que destacar em cada etapa e plano de contingência.
- `tests/test_demo_script.py`: o roteiro de demonstração executado pelos serviços, para garantir que cada passo descrito funciona com os dados de demonstração.
- `docs/ACADEMIC_REPORT.md`: relatório técnico (objetivo, requisitos, metodologia com OpenSpec, arquitetura, modelagem, segurança, qualidade, limitações e trabalhos futuros) com métricas medidas.
- Medição de cobertura de testes com `pytest-cov` (dependência de desenvolvimento) e registro do resultado.
- Revisão de `README.md`, `docs/PROJECT.md` e `docs/OPEN_SPEC_APPROACH.md` para refletir o estado atual.

## Capabilities

### New Capabilities

- Nenhuma (mudança de documentação e verificação; `skip_specs: true`).

### Modified Capabilities

- Nenhuma.

## Impact

- **Documentação:** novos documentos em `docs/` e revisão dos existentes.
- **Testes:** um teste de ponta a ponta do roteiro pelos serviços.
- **Dependências de desenvolvimento:** `pytest-cov` em `requirements-dev.txt`.
- **Código da aplicação:** nenhuma alteração prevista.

## Out of Scope

- Novas funcionalidades e a integração real com o Xano (aguarda documentação).
- Arquivamento das mudanças anteriores (depende de autorização do usuário).
