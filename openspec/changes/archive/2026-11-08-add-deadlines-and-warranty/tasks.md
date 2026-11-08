# Tasks

## 1. Domínio e serviço

- [x] 1.1 Acrescentar `due_date` e `warranty_of` aos modelos, `domain/deadlines.py` (atraso, entrega, garantia, elegibilidade) e o total sem cobrança das ordens em garantia em `compute_totals`; verificar com testes de domínio.
- [x] 1.2 Em `OrderService`: previsão padrão e validação na abertura, `set_due_date` com histórico e `open_warranty`; verificar com testes de serviço sobre a demonstração.

## 2. Backend Xano

- [x] 2.1 Acrescentar `previsao_entrega` e `garantia_de` a `os_servicos`, aceitar e validar em `POST`/`PATCH`, incluir `_garantia` nas leituras e `previsao_entrega` na consulta pública; validar pelo Developer MCP, atualizar o contrato-alvo e enviar após autorização.
- [x] 2.2 Mapear os novos campos no adaptador; verificar com testes sobre servidor simulado e com `python -m tools.xano_contract_check`.

## 3. Interface

- [x] 3.1 Previsão na abertura e no detalhe (com alteração), selo "Atrasada" na lista e no detalhe, alerta no painel, "Garantia até", "Abrir ordem em garantia" e "Ordem em garantia da …"; previsão e garantia no portal e previsão na consulta pública; verificar no navegador.

## 4. Verificação

- [x] 4.1 Executar `pytest`, `openspec validate add-deadlines-and-warranty --strict` e o roteiro no Xano real, registrando os resultados.

## Registro de verificação (2026-11-07/08)

- **pytest (.venv):** 406 passed in 69.95s (0:01:09) (12 testes novos em `tests/test_deadlines_warranty.py`; testes de presenters, consulta pública e abertura no Xano atualizados).
- **OpenSpec:** `openspec validate add-deadlines-and-warranty --strict` válido.
- **XanoScript:** 59 arquivos válidos no Developer MCP; envio após simulação e autorização; verificador: 34 de 34.
- **Regras no Xano real** (API, contas de teste):
  - abertura sem previsão → previsão = hoje + 7 dias; previsão no passado → "A previsão de entrega não pode ser anterior à data de abertura.";
  - técnico responsável alterando a previsão → 403 "O perfil tecnico não tem permissão para alterar a previsão de entrega."; atendente → previsão alterada;
  - garantia da OS-2026-00001 (concluída e entregue) → aceita, com `garantia_de` e `_garantia` na leitura;
  - garantia de ordem cancelada ou ainda em reparo → "Só ordens concluídas e entregues têm garantia.";
  - consulta pública com `previsao_entrega`.
  - Ordens de teste OS-2026-00005 e OS-2026-00006 canceladas ao final.
- **Navegador (modo demonstração):** alerta "4 ordem(ns) atrasada(s)" no painel; coluna "Previsão" e selos "Atrasada há N dias" (ordem concluída sem selo); "Garantia até 02/01/2027" na OS-2026-00120; abertura em garantia (OS-2026-00127) com selo "Garantia", vínculo à original e histórico; alteração da previsão para 20/11/2026 removendo o atraso. Corrigido o espaçamento entre "Previsão de entrega" e "Garantia até".
