// Pagamentos recebidos por ordem de serviço.
table "pagamento" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int os_servicos_id {
      table = "os_servicos"
    }
    decimal valor_a_ser_pago filters=min:0.01
    text forma_de_pagamento filters=trim {
      description = "Dinheiro, PIX, Cartão de débito ou Cartão de crédito"
    }
    date data_do_pagamento
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "os_servicos_id"}]}
  ]
}
