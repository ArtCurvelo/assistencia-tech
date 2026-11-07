// Itens do orçamento da ordem de serviço (serviços e peças).
table "os_itens" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int os_servicos_id {
      table = "os_servicos"
    }
    enum tipo {
      values = ["servico", "peca"]
    }
    text descricao filters=trim
    int quantidade?=1 filters=min:1
    decimal valor_unitario filters=min:0.01
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "os_servicos_id"}]}
  ]
}
