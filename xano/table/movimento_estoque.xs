// Movimentações de estoque (somente inclusão): entrada, saída por ordem e devolução.
table "movimento_estoque" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int peca_id {
      table = "peca"
    }
    enum tipo {
      values = ["entrada", "saida", "devolucao"]
    }
    int quantidade filters=min:1
    int? os_servicos_id? {
      table = "os_servicos"
    }
    text autor filters=trim
    text? observacao? filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "peca_id"}]}
  ]
  guid = "mu6HFfa0ZuR0xPhcQR9vTK8Wtz4"
}
