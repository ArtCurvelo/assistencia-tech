# Tasks

## 1. Domínio e serviço

- [x] 1.1 Acrescentar `due_date` e `warranty_of` aos modelos, `domain/deadlines.py` (atraso, entrega, garantia, elegibilidade) e o total sem cobrança das ordens em garantia em `compute_totals`; verificar com testes de domínio.
- [x] 1.2 Em `OrderService`: previsão padrão e validação na abertura, `set_due_date` com histórico e `open_warranty`; verificar com testes de serviço sobre a demonstração.

## 2. Backend Xano

- [ ] 2.1 Acrescentar `previsao_entrega` e `garantia_de` a `os_servicos`, aceitar e validar em `POST`/`PATCH`, incluir `_garantia` nas leituras e `previsao_entrega` na consulta pública; validar pelo Developer MCP, atualizar o contrato-alvo e enviar após autorização.
- [ ] 2.2 Mapear os novos campos no adaptador; verificar com testes sobre servidor simulado e com `python -m tools.xano_contract_check`.

## 3. Interface

- [x] 3.1 Previsão na abertura e no detalhe (com alteração), selo "Atrasada" na lista e no detalhe, alerta no painel, "Garantia até", "Abrir ordem em garantia" e "Ordem em garantia da …"; previsão e garantia no portal e previsão na consulta pública; verificar no navegador.

## 4. Verificação

- [ ] 4.1 Executar `pytest`, `openspec validate add-deadlines-and-warranty --strict` e o roteiro no Xano real, registrando os resultados.
