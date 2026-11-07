# Tasks

## 1. Métricas

- [x] 1.1 Adicionar `pytest-cov` a `requirements-dev.txt` e medir a cobertura das camadas `domain`, `services`, `data` e `models`; verificar registrando o resultado deste comando neste arquivo.
- [x] 1.2 Levantar contagem de arquivos, linhas, testes e requisitos rastreados; verificar com os comandos registrados neste arquivo.

## 2. Roteiro de demonstração

- [x] 2.1 Escrever `tests/test_demo_script.py`, que executa os passos do roteiro pelos serviços com os perfis reais; verificar com `pytest`.
- [x] 2.2 Escrever `docs/DEMO_SCRIPT.md` com os mesmos passos, contas, tempos e destaques; verificar conferindo cada passo com o teste da tarefa 2.1.

## 3. Documentação técnica

- [x] 3.1 Escrever `docs/ARCHITECTURE.md` com diagramas de camadas e de sequência; verificar conferindo módulos e nomes citados com o código.
- [x] 3.2 Escrever `docs/ACADEMIC_REPORT.md` com as métricas medidas; verificar conferindo cada número com o registro das tarefas 1.1 e 1.2.
- [x] 3.3 Revisar `README.md`, `docs/PROJECT.md` e `docs/OPEN_SPEC_APPROACH.md`; verificar que não há afirmações desatualizadas (busca por "não utiliza", "protótipo", "demonstrativo" e mudanças listadas).

## 4. Verificação

- [x] 4.1 Executar `pytest`, `openspec validate --all --strict` e registrar os resultados neste arquivo.

## Registro de verificação (2026-11-06)

**Métricas (comandos executados na `.venv`):**
- `python -m pytest -q` → 313 aprovados, 0 falhas (15 arquivos de teste).
- `python -m pytest --cov=assistencia_tech.domain --cov=assistencia_tech.services --cov=assistencia_tech.data --cov=assistencia_tech.models --cov=assistencia_tech.presenters --cov=assistencia_tech.config` → 1.854 instruções, 56 não executadas, **97%**.
- `python -m pytest --cov=assistencia_tech` → 2.988 instruções, 921 não executadas, **69%** (páginas, componentes e estados Reflex sem testes automatizados).
- Arquivos Python da aplicação: 66, com 5.421 linhas não vazias; maior arquivo: 347 linhas (`presenters.py`).
- Especificações: 12 capacidades, 88 requisitos e 141 cenários (`grep` de `### Requirement:` e `#### Scenario:` em `openspec/specs` e `openspec/changes`, sem o arquivo); `docs/REQUIREMENTS.md`: 32 RF e 14 RNF.
- `openspec validate --all --strict` → 8 itens válidos.

**Roteiro de demonstração:** `tests/test_demo_script.py` executa os passos 1 a 9 de `docs/DEMO_SCRIPT.md` (consulta pública, login com mensagem genérica, cadastro da cliente, abertura da OS-2026-00127 pelo atendente, diagnóstico e orçamento pelo técnico, aprovação, conclusão, pagamentos e entrega, portal, relatórios com R$ 655,00 recebidos e CSV, regras de colaboradores) e passou. Os passos 10 e 11 (responsividade e terminal) correspondem a verificações já registradas nas fases 4 e anteriores.

**Revisão de documentos:** `README.md`, `docs/PROJECT.md` e `docs/OPEN_SPEC_APPROACH.md` sem ocorrências de "protótipo" ou "não utiliza"; estado de cada mudança atualizado.

**Não executado:** o roteiro não foi percorrido de ponta a ponta no navegador nesta fase; os passos foram verificados individualmente no navegador nas fases 2 a 5 e, em conjunto, pelos serviços.

## Workflow follow-up

- Arquivar as mudanças concluídas após autorização do usuário.
