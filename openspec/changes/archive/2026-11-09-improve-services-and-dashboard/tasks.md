# Tasks

## 1. Site público

- [x] 1.1 Tirar o botão "Área administrativa" da página inicial.
- [x] 1.2 Ampliar a página de serviços: etapas do atendimento, compromissos, perguntas frequentes e chamadas.

## 2. Painel

- [x] 2.1 Presenters `attention_rows`, `technician_queue` e "recebido no mês"; verificar com testes.
- [x] 2.2 Saudação, atalhos por permissão, "Precisa de atenção", "Meus atendimentos" e o novo indicador.

## 3. Verificação

- [x] 3.1 Executar `pytest` e `openspec validate --strict`; conferir no navegador com os perfis Administrador e Técnico e na página de serviços.

## Registro de verificação (2026-11-09)

- **pytest (.venv):** 445 passed (6 testes novos em `tests/test_admin_dashboard.py`).
- **Navegador (modo demonstração):**
  - página inicial sem "Área administrativa"; no lugar, "Acompanhar meu reparo" (âncora `#consulta`);
  - serviços: 6 etapas, 4 compromissos, 6 perguntas frequentes (abrem e fecham), chamadas para `/#consulta` e `/cadastro`;
  - Administrador: "Bom dia, Ana!", "segunda-feira, 9 de novembro de 2026 · Administrador", 4 atalhos, "Recebido no mês" R$ 0,00 (os pagamentos do seed são de outubro) e "Precisa de atenção" com 4 atrasadas (21, 19, 18 e 16 dias) e 1 pronta para entrega; a OS-2026-00123, aguardando aprovação e atrasada, aparece uma vez, como atrasada;
  - Técnico (Carlos): só o atalho "Estoque" e "Meus atendimentos" com OS-2026-00123 e OS-2026-00125, a mais antiga primeiro.
