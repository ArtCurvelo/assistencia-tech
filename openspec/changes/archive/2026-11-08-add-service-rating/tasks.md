# Tasks

## 1. Domínio e serviço

- [x] 1.1 Criar `Rating` no modelo da ordem, `domain/rating.py` (validação, classificação, NPS) e os indicadores em `domain/reports.py`; verificar com testes de domínio.
- [x] 1.2 Criar a permissão `portal.rate_service` (Cliente) e `PortalService.rate`; gravar na demonstração; verificar com testes de serviço.

## 2. Backend Xano

- [x] 2.1 Criar a tabela `avaliacao`, o addon `atech_avaliacao_da_os`, o endpoint `POST /portal/avaliacao` e o `_avaliacao` nas leituras das ordens; validar pelo Developer MCP, atualizar o contrato-alvo e enviar após autorização.
- [x] 2.2 Mapear a avaliação no adaptador e gravar pelo endpoint novo; verificar com testes sobre servidor simulado e com `python -m tools.xano_contract_check`.

## 3. Interface

- [x] 3.1 Formulário de avaliação no portal, avaliação no detalhe da ordem, seção de satisfação nos relatórios e indicador no painel; verificar no navegador.

## 4. Verificação

- [x] 4.1 Executar `pytest`, `openspec validate add-service-rating --strict` e o roteiro no Xano real, registrando os resultados.

## Registro de verificação (2026-11-08)

- **pytest (.venv):** 431 passed (10 testes novos em `tests/test_service_rating.py`; matriz de permissões e métricas vazias atualizadas).
- **OpenSpec:** `openspec validate add-service-rating --strict` válido.
- **XanoScript:** 62 arquivos válidos no Developer MCP; envio após simulação e autorização (62 documentos); verificador: 35 de 35, com `_avaliacao` nas leituras.
- **Regras no Xano real** (API, contas de teste):
  - ordem em reparo → 400 "Só ordens entregues podem ser avaliadas.";
  - nota 11 → 400 "A nota deve ser um número inteiro de 0 a 10."; comentário com 501 caracteres → 400 "O comentário deve ter no máximo 500 caracteres.";
  - atendente → 403 "Seu perfil não tem permissão para esta ação.";
  - cliente avalia a OS-2026-00001 entregue com nota 9 → 200; segunda avaliação → 400 "Esta ordem já foi avaliada.";
  - `_avaliacao` presente em `portal/minhas_ordens` (só na OS 1) e em `os_servicos/1` para a atendente.
- **Navegador (modo demonstração):**
  - painel com "NPS (90 dias)" +100 e 1 avaliação; detalhe da OS-2026-00120 com nota 9, "Promotor" e o comentário;
  - administrador conclui, recebe e entrega a OS-2026-00125; a cliente Marina vê "Avalie o atendimento", escolhe 8, comenta e envia → "Obrigado pela sua avaliação!" e "Sua avaliação" no lugar do formulário;
  - relatórios com NPS, nota média, promotores, neutros, detratores, "Nota média" por técnico (9,0 para Diego Martins) e o comentário recente.
- **Dado de teste no Xano:** avaliação nota 9 da OS-2026-00001 ("Avaliação de teste do roteiro de verificação."), imutável pela API.
