query "pagamentos" verb=POST {
  api_group = "atech_os"
  description = "Admin e atendente: registra um pagamento, sem exceder o saldo e nunca em ordens canceladas."
  auth = "user"
  input {
    int os_servicos_id {
      table = "os_servicos"
    }
    decimal valor_a_ser_pago filters=min:0.01
    text forma_de_pagamento filters=trim
    date data_do_pagamento
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $ordem
    precondition ($ordem != null) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    precondition ($ordem.status != "cancelado") {
      error_type = "inputerror"
      error = "Não é possível registrar pagamentos em ordens canceladas."
    }
    precondition (["Dinheiro", "PIX", "Cartão de débito", "Cartão de crédito"]|in:$input.forma_de_pagamento) {
      error_type = "inputerror"
      error = "Forma de pagamento inválida. Use Dinheiro, PIX, Cartão de débito ou Cartão de crédito."
    }
    function.run "atech_saldo_da_os" {
      input = {os_servicos_id: $ordem.id}
    } as $totais
    precondition ($totais.total > 0) {
      error_type = "inputerror"
      error = "A ordem não possui valores no orçamento para receber pagamento."
    }
    precondition ($input.valor_a_ser_pago <= $totais.saldo) {
      error_type = "inputerror"
      error = "O pagamento excede o saldo devedor da ordem."
    }
    db.add "pagamento" {
      data = {
        os_servicos_id: $input.os_servicos_id,
        valor_a_ser_pago: $input.valor_a_ser_pago,
        forma_de_pagamento: $input.forma_de_pagamento,
        data_do_pagamento: $input.data_do_pagamento
      }
    } as $pagamento
    db.edit "os_servicos" {
      field_name = "id"
      field_value = $ordem.id
      data = {atualizado_em: now}
    }
  }
  response = $pagamento
  guid = "DSRq-UXwuvItcmiOlGwumqS8ZNc"
}
