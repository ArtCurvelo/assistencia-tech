# Design: Prazos e garantia

## Decisions

### D1. Regras em `domain/deadlines.py`

Funções puras recebem a data de hoje: `is_overdue(ordem, hoje)` (antes de Concluído e com previsão vencida), `days_late`, `delivered_at` (último evento do histórico para "Entregue"), `warranty_until` (entrega + 90 dias, somente se a ordem passou por "Concluído") e `ensure_warranty_eligible` (ordem entregue, dentro do prazo, mesmo cliente e equipamento). A data da entrega vem do histórico, que já é imutável, sem campo novo.

### D2. Previsão padrão e validação

Sem previsão informada, a abertura usa a data de abertura + 7 dias. A previsão não pode ser anterior à data de abertura. A alteração usa a permissão de atribuir técnico (`orders.assign`, Administrador e Atendente), registra "Previsão de entrega alterada para dd/mm/aaaa." no histórico e é recusada em ordens Entregues ou Canceladas.

### D3. Garantia sem cobrança

A ordem em garantia guarda o código da ordem original (`warranty_of`). Em `compute_totals`, uma ordem em garantia tem total, saldo e situação de pagamento "Garantia": os itens continuam no orçamento (inclusive a baixa de peças do estoque), mas nada é cobrado; pagamentos são recusados porque não há valor a receber, e a entrega não exige quitação.

### D4. Abertura a partir da ordem original

O detalhe da ordem original oferece "Abrir ordem em garantia" enquanto houver garantia; a nova ordem usa o mesmo cliente e equipamento, e o histórico de abertura cita a ordem original. O backend repete a verificação (ordem original entregue há no máximo 90 dias, mesmo cliente e equipamento).

### D5. Xano

`os_servicos` ganha `previsao_entrega` (date) e `garantia_de` (id da ordem original). As listagens e o detalhe trazem o *addon* `_garantia` (id e `created_at` da original) para a aplicação montar o código `OS-AAAA-NNNNN`. A consulta pública passa a devolver `previsao_entrega`.

## Risks / Trade-offs

- [Atraso calculado pela data do servidor da aplicação] → horário de Brasília (`domain.clock`), o mesmo usado nas demais datas.
- [Garantia por histórico] → ordens entregues antes desta mudança também têm garantia calculada, porque o histórico de status já existe.
